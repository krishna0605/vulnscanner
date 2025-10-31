"""
Web spider component for making async HTTP requests with rate limiting,
error handling, and robots.txt compliance.
"""

import asyncio
import logging
import time
from typing import Dict, Optional, Set
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import aiohttp
from aiohttp import ClientTimeout, ClientError

from ..schemas.sqlite_dashboard import ScanConfiguration

logger = logging.getLogger(__name__)


class WebSpider:
    """
    Async web spider for fetching URLs with rate limiting and error handling.
    Handles robots.txt compliance, session management, and response processing.
    """
    
    def __init__(self, config: ScanConfiguration):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.robots_cache: Dict[str, RobotFileParser] = {}
        self.failed_domains: Set[str] = set()
        
        # Configure timeout
        self.timeout = ClientTimeout(
            total=config.timeout,
            connect=10,
            sock_read=config.timeout
        )
        
        # Configure headers
        self.headers = {
            'User-Agent': config.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    async def initialize(self):
        """Initialize the HTTP session."""
        if not self.session:
            connector = aiohttp.TCPConnector(
                limit=100,  # Total connection pool size
                limit_per_host=10,  # Max connections per host
                ttl_dns_cache=300,  # DNS cache TTL
                use_dns_cache=True,
            )
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=self.timeout,
                headers=self.headers
            )
    
    async def close(self):
        """Close the HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def fetch_url(self, url: str) -> Optional[Dict]:
        """
        Fetch a single URL and return response data.
        
        Args:
            url: URL to fetch
            
        Returns:
            Dict with response data or None if failed
        """
        if not self.session:
            await self.initialize()
        
        # Check robots.txt if enabled
        if self.config.respect_robots and not await self._can_fetch(url):
            logger.debug(f"Robots.txt disallows fetching: {url}")
            return None
        
        # Skip failed domains
        domain = urlparse(url).netloc
        if domain in self.failed_domains:
            return None
        
        start_time = time.time()
        
        try:
            async with self.session.get(url, allow_redirects=self.config.follow_redirects) as response:
                # Calculate response time
                response_time = int((time.time() - start_time) * 1000)
                
                # Read content with size limit
                content = await self._read_content_safely(response)
                
                # Extract title from HTML
                title = None
                if response.content_type and 'text/html' in response.content_type:
                    title = self._extract_title(content)
                
                return {
                    'url': str(response.url),
                    'status_code': response.status,
                    'content_type': response.content_type,
                    'content_length': len(content) if content else 0,
                    'response_time': response_time,
                    'headers': dict(response.headers),
                    'content': content,
                    'title': title,
                    'final_url': str(response.url)  # After redirects
                }
        
        except asyncio.TimeoutError:
            logger.warning(f"Timeout fetching {url}")
            return None
        
        except ClientError as e:
            logger.warning(f"Client error fetching {url}: {e}")
            # Mark domain as problematic after multiple failures
            self._handle_domain_failure(domain)
            return None
        
        except Exception as e:
            logger.error(f"Unexpected error fetching {url}: {e}")
            return None
    
    async def _read_content_safely(self, response: aiohttp.ClientResponse) -> Optional[str]:
        """
        Safely read response content with size limits.
        
        Args:
            response: aiohttp response object
            
        Returns:
            Content as string or None if too large/error
        """
        try:
            # Check content length
            content_length = response.headers.get('Content-Length')
            if content_length and int(content_length) > 10 * 1024 * 1024:  # 10MB limit
                logger.warning(f"Content too large: {content_length} bytes")
                return None
            
            # Read content with size limit
            content_bytes = await response.read()
            if len(content_bytes) > 10 * 1024 * 1024:  # 10MB limit
                logger.warning(f"Content too large after reading: {len(content_bytes)} bytes")
                return None
            
            # Decode content
            try:
                content = content_bytes.decode('utf-8', errors='ignore')
            except UnicodeDecodeError:
                # Try other common encodings
                for encoding in ['latin1', 'cp1252', 'iso-8859-1']:
                    try:
                        content = content_bytes.decode(encoding, errors='ignore')
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    logger.warning(f"Could not decode content for {response.url}")
                    return None
            
            return content
        
        except Exception as e:
            logger.error(f"Error reading content: {e}")
            return None
    
    def _extract_title(self, content: str) -> Optional[str]:
        """
        Extract page title from HTML content.
        
        Args:
            content: HTML content
            
        Returns:
            Page title or None
        """
        try:
            import re
            title_match = re.search(r'<title[^>]*>([^<]+)</title>', content, re.IGNORECASE)
            if title_match:
                title = title_match.group(1).strip()
                # Clean up title
                title = re.sub(r'\\s+', ' ', title)
                return title[:500]  # Limit title length
        except Exception as e:
            logger.debug(f"Error extracting title: {e}")
        
        return None
    
    async def _can_fetch(self, url: str) -> bool:
        """
        Check if URL can be fetched according to robots.txt.
        
        Args:
            url: URL to check
            
        Returns:
            True if URL can be fetched
        """
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            
            # Check cache first
            if domain in self.robots_cache:
                rp = self.robots_cache[domain]
                return rp.can_fetch(self.config.user_agent, url)
            
            # Fetch robots.txt
            robots_url = f"{parsed_url.scheme}://{domain}/robots.txt"
            
            try:
                async with self.session.get(robots_url, timeout=ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        robots_content = await response.text()
                        
                        # Parse robots.txt
                        rp = RobotFileParser()
                        rp.set_url(robots_url)
                        rp.read_robots_txt(robots_content)
                        
                        # Cache the parser
                        self.robots_cache[domain] = rp
                        
                        return rp.can_fetch(self.config.user_agent, url)
            
            except Exception as e:
                logger.debug(f"Could not fetch robots.txt for {domain}: {e}")
            
            # If robots.txt is not available or failed to parse, allow fetching
            return True
        
        except Exception as e:
            logger.error(f"Error checking robots.txt for {url}: {e}")
            return True
    
    def _handle_domain_failure(self, domain: str):
        """
        Handle domain failure by tracking failed attempts.
        
        Args:
            domain: Domain that failed
        """
        # For now, just log the failure
        # In a more sophisticated implementation, we could track failure counts
        # and temporarily blacklist domains with too many failures
        logger.warning(f"Domain failure recorded for: {domain}")
    
    async def fetch_multiple_urls(self, urls: list[str], max_concurrent: int = 10) -> Dict[str, Optional[Dict]]:
        """
        Fetch multiple URLs concurrently.
        
        Args:
            urls: List of URLs to fetch
            max_concurrent: Maximum concurrent requests
            
        Returns:
            Dict mapping URLs to their response data
        """
        if not self.session:
            await self.initialize()
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def fetch_with_semaphore(url: str) -> tuple[str, Optional[Dict]]:
            async with semaphore:
                result = await self.fetch_url(url)
                return url, result
        
        # Create tasks for all URLs
        tasks = [fetch_with_semaphore(url) for url in urls]
        
        # Execute all tasks
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        url_results = {}
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Error in concurrent fetch: {result}")
                continue
            
            url, response_data = result
            url_results[url] = response_data
        
        return url_results
    
    async def head_request(self, url: str) -> Optional[Dict]:
        """
        Make a HEAD request to get headers without content.
        
        Args:
            url: URL to check
            
        Returns:
            Dict with response headers or None if failed
        """
        if not self.session:
            await self.initialize()
        
        try:
            async with self.session.head(url, allow_redirects=self.config.follow_redirects) as response:
                return {
                    'url': str(response.url),
                    'status_code': response.status,
                    'content_type': response.content_type,
                    'content_length': response.headers.get('Content-Length'),
                    'headers': dict(response.headers),
                    'final_url': str(response.url)
                }
        
        except Exception as e:
            logger.debug(f"HEAD request failed for {url}: {e}")
            return None