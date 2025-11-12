"""
Main async crawling orchestrator for web vulnerability scanning.
Handles URL discovery, rate limiting, and data extraction coordination.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Set
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass, field
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from .spider import WebSpider
from .parser import HTMLParser
from .normalizer import URLNormalizer
from .session import SessionManager
from .fingerprinter import TechnologyFingerprinter
from ..models.unified_models import ScanSession, DiscoveredUrl, ExtractedForm, TechnologyFingerprint
from ..schemas.dashboard import ScanConfigurationSchema

logger = logging.getLogger(__name__)


@dataclass
class CrawlStats:
    """Statistics tracking for crawl session."""
    urls_discovered: int = 0
    urls_crawled: int = 0
    forms_found: int = 0
    technologies_detected: int = 0
    errors: int = 0
    start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    end_time: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        return {
            "urls_discovered": self.urls_discovered,
            "urls_crawled": self.urls_crawled,
            "forms_found": self.forms_found,
            "technologies_detected": self.technologies_detected,
            "errors": self.errors,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": (
                (self.end_time - self.start_time).total_seconds() 
                if self.end_time and self.start_time else None
            )
        }


class CrawlerEngine:
    """
    Main crawler engine that orchestrates the entire scanning process.
    Manages URL queue, rate limiting, and coordinates all extraction components.
    """
    
    def __init__(self, config: ScanConfigurationSchema, session_id: int, db_session: AsyncSession):
        self.config = config
        self.session_id = session_id
        self.db_session = db_session
        
        # Core components
        self.spider = WebSpider(config)
        self.parser = HTMLParser()
        self.normalizer = URLNormalizer()
        # Session manager will be wired to the spider's aiohttp session after initialization
        self.session_manager = SessionManager()
        self.fingerprinter = TechnologyFingerprinter()
        
        # Crawl state
        self.url_queue: asyncio.Queue = asyncio.Queue()
        self.visited_urls: Set[str] = set()
        self.discovered_urls: Set[str] = set()
        self.stats = CrawlStats()
        
        # Concurrency control
        self.semaphore = asyncio.Semaphore(config.max_concurrent_requests or 10)
        self.domain_semaphores: Dict[str, asyncio.Semaphore] = {}
        
        # Rate limiting
        self.rate_limiter = asyncio.Semaphore(config.requests_per_second or 10)
        self.last_request_time = 0.0
        
        # Control flags
        self.is_running = False
        self.should_stop = False
        
    async def start_crawl(self, target_url: str) -> CrawlStats:
        """
        Start the crawling process from the target URL.
        
        Args:
            target_url: The initial URL to start crawling from
            
        Returns:
            CrawlStats: Final statistics of the crawl session
        """
        logger.info(f"Starting crawl for session {self.session_id} with target: {target_url}")
        
        self.is_running = True
        self.stats.start_time = datetime.now(timezone.utc)
        
        try:
            # Initialize HTTP session via spider and wire session manager
            await self.spider.initialize()
            self.session_manager.session = self.spider.session
            
            # Configure authentication if provided
            if self.config.authentication:
                try:
                    await self.session_manager.configure_authentication(self.config.authentication, target_url)
                except Exception as auth_exc:
                    logger.error(f"Authentication configuration failed: {auth_exc}")
            
            # Normalize and add initial URL
            normalized_url = self.normalizer.normalize_url(target_url)
            await self.url_queue.put((normalized_url, 0))  # (url, depth)
            self.discovered_urls.add(normalized_url)
            self.stats.urls_discovered = 1
            
            # Update scan session status
            await self._update_scan_status("running")
            
            # Start crawler workers
            worker_count = min(5, self.config.max_concurrent_requests or 5)
            workers = [
                asyncio.create_task(self._crawler_worker(f"worker-{i}"))
                for i in range(worker_count)
            ]

            # Wait for queue to be fully processed to avoid premature termination
            await self.url_queue.join()

            # Signal workers to stop and wait for them
            self.should_stop = True
            for w in workers:
                w.cancel()
            await asyncio.gather(*workers, return_exceptions=True)
            
        except Exception as e:
            logger.error(f"Crawl failed for session {self.session_id}: {e}")
            self.stats.errors += 1
            await self._update_scan_status("failed")
            raise
        finally:
            self.is_running = False
            self.stats.end_time = datetime.now(timezone.utc)
            
            # Close session manager
            await self.session_manager.close()
            # Ensure HTTP client session is closed
            try:
                await self.spider.close()
            except Exception as close_exc:
                logger.debug(f"Error closing spider session: {close_exc}")
            
            # Update final statistics
            await self._update_scan_stats()
            
            if not self.should_stop:
                await self._update_scan_status("completed")
            
        logger.info(f"Crawl completed for session {self.session_id}. Stats: {self.stats.to_dict()}")
        return self.stats
    
    async def stop_crawl(self):
        """Stop the crawling process gracefully."""
        logger.info(f"Stopping crawl for session {self.session_id}")
        self.should_stop = True
        await self._update_scan_status("cancelled")
    
    async def _crawler_worker(self, worker_name: str):
        """
        Worker coroutine that processes URLs from the queue.
        
        Args:
            worker_name: Identifier for this worker
        """
        logger.debug(f"Starting crawler worker: {worker_name}")
        
        while not self.should_stop:
            try:
                # Get next URL from queue with timeout
                try:
                    url, depth = await asyncio.wait_for(
                        self.url_queue.get(), timeout=5.0
                    )
                except asyncio.TimeoutError:
                    # If queue appears empty, loop to check stop flag or new work
                    continue
                
                # Skip if already visited or depth exceeded
                if url in self.visited_urls or depth > self.config.max_depth:
                    self.url_queue.task_done()
                    continue
                
                # Process the URL
                await self._process_url(url, depth)
                self.url_queue.task_done()
                
            except Exception as e:
                logger.error(f"Worker {worker_name} error processing URL: {e}")
                self.stats.errors += 1
                # If an error happened after getting an item but before task_done,
                # ensure queue is progressed safely.
                if not self.url_queue.empty():
                    try:
                        self.url_queue.task_done()
                    except Exception:
                        pass
        
        logger.debug(f"Crawler worker {worker_name} finished")
    
    async def _process_url(self, url: str, depth: int):
        """
        Process a single URL: fetch, parse, extract data, and discover new URLs.
        
        Args:
            url: URL to process
            depth: Current crawl depth
        """
        if url in self.visited_urls:
            return
        
        # Apply rate limiting
        await self._apply_rate_limit(url)
        
        # Use semaphore for concurrency control
        async with self.semaphore:
            try:
                # Mark as visited
                self.visited_urls.add(url)
                
                # Fetch the URL
                response_data = await self.spider.fetch_url(url)
                if not response_data:
                    return
                
                self.stats.urls_crawled += 1
                
                # Store discovered URL in database
                await self._store_discovered_url(url, response_data, depth)
                
                # Parse HTML content if applicable
                if response_data.get('content_type', '').startswith('text/html'):
                    await self._parse_html_content(url, response_data, depth)
                
                # Technology fingerprinting
                await self._perform_fingerprinting(url, response_data)
                
            except Exception as e:
                logger.error(f"Error processing URL {url}: {e}")
                self.stats.errors += 1
    
    async def _parse_html_content(self, url: str, response_data: Dict, depth: int):
        """
        Parse HTML content and extract forms and links.
        
        Args:
            url: Source URL
            response_data: Response data from spider
            depth: Current crawl depth
        """
        try:
            html_content = response_data.get('content', '')
            if not html_content:
                return
            
            # Parse HTML
            parsed_data = await self.parser.parse_html(html_content, url)
            
            # Extract and store forms
            if parsed_data.get('forms'):
                await self._store_forms(url, parsed_data['forms'])
                self.stats.forms_found += len(parsed_data['forms'])
            
            # Discover new URLs from links
            if depth < self.config.max_depth:
                await self._discover_urls(url, parsed_data.get('links', []), depth + 1)
            
        except Exception as e:
            logger.error(f"Error parsing HTML for {url}: {e}")
            self.stats.errors += 1
    
    async def _discover_urls(self, base_url: str, links: List[str], depth: int):
        """
        Discover and queue new URLs from extracted links.
        
        Args:
            base_url: Base URL for resolving relative links
            links: List of discovered links
            depth: Depth for new URLs
        """
        for link in links:
            try:
                # Extract URL from link dict or use as string
                link_url = link.get('url') if isinstance(link, dict) else link
                
                # Resolve relative URLs
                absolute_url = urljoin(base_url, link_url)
                normalized_url = self.normalizer.normalize_url(absolute_url)
                
                # Check if URL is valid for crawling (excludes certain file types)
                if not self.normalizer.is_valid_url(normalized_url):
                    continue
                
                # Check if URL is in scope
                if not self._is_url_in_scope(normalized_url):
                    continue
                
                # Skip if already discovered
                if normalized_url in self.discovered_urls:
                    continue
                
                # Add to queue and discovered set
                self.discovered_urls.add(normalized_url)
                await self.url_queue.put((normalized_url, depth))
                self.stats.urls_discovered += 1
                
                # Respect max_pages limit
                if len(self.discovered_urls) >= self.config.max_pages:
                    logger.info(f"Reached max_pages limit: {self.config.max_pages}")
                    self.should_stop = True
                    break
                
            except Exception as e:
                logger.error(f"Error processing link {link}: {e}")
    
    def _is_url_in_scope(self, url: str) -> bool:
        """
        Check if URL is within the configured scope.
        
        Args:
            url: URL to check
            
        Returns:
            bool: True if URL is in scope
        """
        urlparse(url)
        
        # Check scope patterns
        if self.config.scope_patterns:
            for pattern in self.config.scope_patterns:
                if pattern in url:
                    return True
            return False
        
        # Default: same domain as target
        return True
    
    async def _apply_rate_limit(self, url: str):
        """
        Apply rate limiting per domain and globally.
        
        Args:
            url: URL being processed
        """
        # Global rate limiting with lock to prevent race conditions
        async with self.rate_limiter:
            async with asyncio.Lock():  # Add lock to prevent race conditions
                current_time = time.time()
                time_since_last = current_time - self.last_request_time
                min_interval = 1.0 / self.config.requests_per_second
                
                if time_since_last < min_interval:
                    await asyncio.sleep(min_interval - time_since_last)
                
                self.last_request_time = time.time()
        
        # Per-domain rate limiting
        domain = urlparse(url).netloc
        if domain not in self.domain_semaphores:
            self.domain_semaphores[domain] = asyncio.Semaphore(5)  # Max 5 concurrent per domain
        
        await self.domain_semaphores[domain].acquire()
        # Release will happen automatically when context exits
    
    async def _store_discovered_url(self, url: str, response_data: Dict, depth: int):
        """Store discovered URL in database."""
        try:
            discovered_url = DiscoveredUrl(
                session_id=self.session_id,
                url=url,
                method="GET",
                status_code=response_data.get('status_code'),
                content_type=response_data.get('content_type'),
                content_length=response_data.get('content_length'),
                response_time=response_data.get('response_time'),
                page_title=response_data.get('title'),
            )
            
            self.db_session.add(discovered_url)
            await self.db_session.commit()
            
        except Exception as e:
            logger.error(f"Error storing discovered URL {url}: {e}")
            await self.db_session.rollback()
    
    async def _store_forms(self, url: str, forms: List[Dict]):
        """Store extracted forms in database."""
        try:
            # Get the URL record
            from sqlalchemy import select
            url_query = select(DiscoveredUrl).where(
                DiscoveredUrl.session_id == self.session_id,
                DiscoveredUrl.url == url
            )
            result = await self.db_session.execute(url_query)
            url_record = result.scalar_one_or_none()
            
            if not url_record:
                return
            
            for form_data in forms:
                extracted_form = ExtractedForm(
                    url_id=url_record.id,
                    form_action=form_data.get('action'),
                    form_method=form_data.get('method', 'GET'),
                    form_fields=form_data.get('fields', {}),
                    csrf_tokens=form_data.get('csrf_tokens', []),
                    authentication_required=form_data.get('auth_required', False)
                )
                
                self.db_session.add(extracted_form)
            
            await self.db_session.commit()
            
        except Exception as e:
            logger.error(f"Error storing forms for {url}: {e}")
            await self.db_session.rollback()
    
    async def _perform_fingerprinting(self, url: str, response_data: Dict):
        """Perform technology fingerprinting and store results."""
        try:
            fingerprint_data = await self.fingerprinter.analyze_response(response_data)
            
            if not fingerprint_data:
                return
            
            # Get the URL record
            from sqlalchemy import select
            url_query = select(DiscoveredUrl).where(
                DiscoveredUrl.session_id == self.session_id,
                DiscoveredUrl.url == url
            )
            result = await self.db_session.execute(url_query)
            url_record = result.scalar_one_or_none()
            
            if not url_record:
                return
            
            tech_fingerprint = TechnologyFingerprint(
                url_id=url_record.id,
                server_software=fingerprint_data.get('server'),
                programming_language=fingerprint_data.get('language'),
                framework=fingerprint_data.get('framework'),
                cms=fingerprint_data.get('cms'),
                javascript_libraries=fingerprint_data.get('js_libraries', []),
                security_headers=fingerprint_data.get('security_headers', {})
            )
            
            self.db_session.add(tech_fingerprint)
            await self.db_session.commit()
            self.stats.technologies_detected += 1
            
        except Exception as e:
            logger.error(f"Error performing fingerprinting for {url}: {e}")
            await self.db_session.rollback()
    
    async def _update_scan_status(self, status: str):
        """Update scan session status in database."""
        try:
            from sqlalchemy import update
            
            stmt = update(ScanSession).where(
                ScanSession.id == self.session_id
            ).values(
                status=status,
                end_time=datetime.now(timezone.utc) if status in ["completed", "failed", "cancelled"] else None
            )
            
            await self.db_session.execute(stmt)
            await self.db_session.commit()
            
        except Exception as e:
            logger.error(f"Error updating scan status: {e}")
            await self.db_session.rollback()
    
    async def _update_scan_stats(self):
        """Update scan session statistics in database."""
        try:
            from sqlalchemy import update
            
            stmt = update(ScanSession).where(
                ScanSession.id == self.session_id
            ).values(
                stats=self.stats.to_dict()
            )
            
            await self.db_session.execute(stmt)
            await self.db_session.commit()
            
        except Exception as e:
            logger.error(f"Error updating scan stats: {e}")
            await self.db_session.rollback()