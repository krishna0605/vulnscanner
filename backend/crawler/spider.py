"""
Web spider component for making async HTTP requests with rate limiting,
error handling, and robots.txt compliance.
"""

import asyncio
import io
import logging
import time
from typing import Dict, Optional, Set
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import aiohttp
from aiohttp import ClientTimeout, ClientError

from ..schemas.dashboard import ScanConfigurationSchema

logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiter for controlling request frequency with proper concurrency support."""
    
    def __init__(self, requests_per_second: int):
        self.requests_per_second = requests_per_second
        self.min_interval = 1.0 / requests_per_second if requests_per_second > 0 else 0
        self.last_request_time = 0
        self._lock = asyncio.Lock()
    
    async def acquire(self):
        """Wait if necessary to respect rate limit."""
        if self.min_interval > 0:
            async with self._lock:
                current_time = time.time()
                time_since_last = current_time - self.last_request_time
                
                if time_since_last < self.min_interval:
                    sleep_time = self.min_interval - time_since_last
                    await asyncio.sleep(sleep_time)
                
                self.last_request_time = time.time()


class WebSpider:
    """
    Async web spider for fetching URLs with rate limiting and error handling.
    Handles robots.txt compliance, session management, and response processing.
    """
    
    def __init__(self, config: ScanConfigurationSchema):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        # robots.txt cache with simple TTL and size eviction
        # domain -> (parser, cached_at_epoch)
        self.robots_cache: Dict[str, tuple[RobotFileParser, float]] = {}
        self.robots_cache_ttl_seconds = 900  # 15 minutes
        self.robots_cache_max_size = 256
        self.failed_domains: Set[str] = set()
        self.rate_limiter = RateLimiter(config.requests_per_second)
        
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
        await self._ensure_session()
    
    async def _ensure_session(self):
        """Ensure HTTP session is created."""
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
    
    async def fetch_url(self, url: str, headers: Optional[Dict] = None, max_retries: int = 0) -> Optional[Dict]:
        """
        Fetch a single URL and return response data.
        
        Args:
            url: URL to fetch
            headers: Optional custom headers
            max_retries: Maximum number of retries for failed requests
            
        Returns:
            Dict with response data or None if failed
        """
        # Ensure session is created
        await self._ensure_session()
        
        # Apply rate limiting
        await self.rate_limiter.acquire()
        
        # Check robots.txt if enabled
        if self.config.respect_robots and not await self._can_fetch(url):
            logger.debug(f"Robots.txt disallows fetching: {url}")
            return None
        
        # Skip failed domains
        domain = urlparse(url).netloc
        if domain in self.failed_domains:
            return None
        
        start_time = time.time()
        
        # Retry loop
        for attempt in range(max_retries + 1):
            try:
                # Merge custom headers with default headers
                request_headers = self.headers.copy()
                if headers:
                    request_headers.update(headers)
                
                async with self.session.get(url, headers=request_headers, allow_redirects=self.config.follow_redirects) as response:
                    # For 5xx errors, retry if we have attempts left
                    if response.status >= 500 and attempt < max_retries:
                        logger.debug(f"Server error {response.status} for {url}, retrying (attempt {attempt + 1}/{max_retries + 1})")
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    
                    # Calculate response time
                    response_time = int((time.time() - start_time) * 1000)
                    
                    # Check content type filtering
                    is_html = response.content_type and 'text/html' in response.content_type
                    
                    # For non-HTML content, return None (filtered out)
                    if not is_html and response.content_type:
                        # Skip non-HTML content types like JSON, images, CSS, etc.
                        non_html_types = ['application/json', 'image/', 'application/pdf', 'text/css', 'text/javascript']
                        if any(content_type in response.content_type for content_type in non_html_types):
                            return None
                    
                    # Read content with size limit
                    content = await self._read_content_safely(response)
                    
                    # Extract title from HTML
                    title = None
                    if is_html:
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
                        'final_url': str(response.url),  # After redirects
                        'is_html': is_html
                    }
            
            except asyncio.TimeoutError:
                if attempt < max_retries:
                    logger.debug(f"Timeout fetching {url}, retrying (attempt {attempt + 1}/{max_retries + 1})")
                    await asyncio.sleep(2 ** attempt)
                    continue
                logger.warning(f"Timeout fetching {url} after {max_retries + 1} attempts")
                return None
            
            except aiohttp.ClientConnectorError as e:
                if attempt < max_retries:
                    logger.debug(f"Connection error fetching {url}, retrying (attempt {attempt + 1}/{max_retries + 1}): {e}")
                    await asyncio.sleep(2 ** attempt)
                    continue
                logger.warning(f"Connection error fetching {url}: {e}")
                return None
            
            except ClientError as e:
                if attempt < max_retries and hasattr(e, 'status') and e.status >= 500:
                    logger.debug(f"Client error {e.status} fetching {url}, retrying (attempt {attempt + 1}/{max_retries + 1})")
                    await asyncio.sleep(2 ** attempt)
                    continue
                logger.warning(f"Client error fetching {url}: {e}")
                # Mark domain as problematic after multiple failures
                self._handle_domain_failure(domain)
                return None
            
            except Exception as e:
                if attempt < max_retries:
                    logger.debug(f"Error fetching {url}, retrying (attempt {attempt + 1}/{max_retries + 1}): {e}")
                    await asyncio.sleep(2 ** attempt)
                    continue
                logger.error(f"Unexpected error fetching {url} after {max_retries + 1} attempts: {e}")
                return None
        
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
                rp, cached_at = self.robots_cache[domain]
                # Evict stale entries
                if (time.time() - cached_at) <= self.robots_cache_ttl_seconds:
                    return rp.can_fetch(self.config.user_agent, url)
                else:
                    # stale entry
                    self.robots_cache.pop(domain, None)
            
            # Fetch robots.txt
            robots_url = f"{parsed_url.scheme}://{domain}/robots.txt"
            
            try:
                async with self.session.get(robots_url, timeout=ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        robots_content = await response.text()
                        
                        # Parse robots.txt
                        rp = RobotFileParser()
                        rp.set_url(robots_url)
                        rp.read_file(io.StringIO(robots_content))
                        
                        # Cache the parser (evict oldest if needed)
                        if len(self.robots_cache) >= self.robots_cache_max_size:
                            # naive eviction: pop an arbitrary item (FIFO not guaranteed with dict; acceptable for simplicity)
                            try:
                                first_key = next(iter(self.robots_cache.keys()))
                                self.robots_cache.pop(first_key, None)
                            except StopIteration:
                                pass
                        self.robots_cache[domain] = (rp, time.time())
                        
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
    
    async def _get_robots_txt(self, domain: str) -> Optional[RobotFileParser]:
        """
        Get robots.txt parser for a domain.
        
        Args:
            domain: Domain to get robots.txt for
            
        Returns:
            RobotFileParser instance or None if failed
        """
        # Check cache first
        if domain in self.robots_cache:
            return self.robots_cache[domain]
        
        await self._ensure_session()
        
        # Fetch robots.txt
        robots_url = f"http://{domain}/robots.txt"
        
        try:
            async with self.session.get(robots_url, timeout=ClientTimeout(total=10)) as response:
                if response.status == 200:
                    robots_content = await response.text()
                    
                    # Parse robots.txt
                    import io
                    rp = RobotFileParser()
                    rp.set_url(robots_url)
                    # Use parse method with StringIO
                    rp.parse(io.StringIO(robots_content).readlines())
                    
                    # Cache the parser
                    self.robots_cache[domain] = (rp, time.time())
                    
                    return rp
        
        except Exception as e:
            logger.debug(f"Could not fetch robots.txt for {domain}: {e}")
        
        return None