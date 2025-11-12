"""
URL normalization and deduplication component.
Ensures consistent URL handling and prevents duplicate crawling.
"""

import logging
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

logger = logging.getLogger(__name__)


class URLNormalizer:
    """
    URL normalizer for consistent URL handling and deduplication.
    Implements various normalization techniques to reduce duplicate URLs.
    """
    
    def __init__(self, excluded_extensions: set[str] | None = None, tracking_params: set[str] | None = None):
        # Common file extensions to exclude (configurable)
        self.excluded_extensions = excluded_extensions or {
            # Images
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico',
            # Documents
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            # Archives
            '.zip', '.rar', '.tar', '.gz', '.7z',
            # Media
            '.mp3', '.mp4', '.avi', '.mov', '.wmv', '.flv',
            # Other
            '.exe', '.dmg', '.pkg', '.deb', '.rpm'
        }
        
        # Parameters to remove during normalization (configurable)
        self.tracking_params = tracking_params or {
            'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
            'gclid', 'fbclid', 'msclkid', '_ga', '_gid', 'ref', 'referrer'
        }
    
    def normalize_url(self, url: str) -> str:
        """
        Normalize a URL for consistent handling.
        
        Args:
            url: Raw URL to normalize
            
        Returns:
            Normalized URL string
        """
        try:
            # Parse the URL
            parsed = urlparse(url.strip())
            
            # Skip if no scheme or netloc
            if not parsed.scheme or not parsed.netloc:
                return url
            
            # Normalize scheme to lowercase
            scheme = parsed.scheme.lower()
            
            # Normalize netloc (domain) to lowercase
            netloc = parsed.netloc.lower()
            
            # Remove default ports
            if ':80' in netloc and scheme == 'http':
                netloc = netloc.replace(':80', '')
            elif ':443' in netloc and scheme == 'https':
                netloc = netloc.replace(':443', '')
            
            # Normalize path
            path = self._normalize_path(parsed.path)
            
            # Normalize query parameters
            query = self._normalize_query(parsed.query)
            
            # Remove fragment (everything after #)
            fragment = ''
            
            # Reconstruct URL
            normalized = urlunparse((scheme, netloc, path, parsed.params, query, fragment))
            
            return normalized
        
        except Exception as e:
            logger.error(f"Error normalizing URL {url}: {e}")
            return url
    
    def _normalize_path(self, path: str) -> str:
        """
        Normalize URL path component.
        
        Args:
            path: URL path
            
        Returns:
            Normalized path
        """
        if not path:
            return '/'
        
        # Remove trailing slash for non-root paths
        if len(path) > 1 and path.endswith('/'):
            path = path.rstrip('/')
        
        # Ensure path starts with /
        if not path.startswith('/'):
            path = '/' + path
        
        # Decode percent-encoded characters that don't need encoding
        import urllib.parse
        try:
            decoded = urllib.parse.unquote(path)
            # Re-encode only necessary characters
            path = urllib.parse.quote(decoded, safe='/:@!$&\'()*+,;=')
        except Exception:
            pass  # Keep original path if decoding fails
        
        return path
    
    def _normalize_query(self, query: str) -> str:
        """
        Normalize query parameters.
        
        Args:
            query: Query string
            
        Returns:
            Normalized query string
        """
        if not query:
            return ''
        
        try:
            # Parse query parameters
            params = parse_qs(query, keep_blank_values=True)
            
            # Remove tracking parameters
            filtered_params = {
                key: value for key, value in params.items()
                if key.lower() not in self.tracking_params
            }
            
            # Sort parameters for consistency
            sorted_params = sorted(filtered_params.items())
            
            # Rebuild query string
            if sorted_params:
                return urlencode(sorted_params, doseq=True)
            else:
                return ''
        
        except Exception as e:
            logger.error(f"Error normalizing query {query}: {e}")
            return query
    
    def is_valid_url(self, url: str) -> bool:
        """
        Check if URL is valid for crawling.
        
        Args:
            url: URL to validate
            
        Returns:
            True if URL is valid for crawling
        """
        try:
            parsed = urlparse(url)
            
            # Must have scheme and netloc
            if not parsed.scheme or not parsed.netloc:
                return False
            
            # Only HTTP/HTTPS
            if parsed.scheme.lower() not in ['http', 'https']:
                return False
            
            # Check for excluded file extensions
            path = parsed.path.lower()
            for ext in self.excluded_extensions:
                if path.endswith(ext):
                    return False
            
            # Skip data URLs, mailto, etc.
            if parsed.scheme.lower() in ['data', 'mailto', 'tel', 'ftp']:
                return False
            
            # Skip very long URLs (potential attack vectors)
            if len(url) > 2000:
                return False
            
            return True
        
        except Exception as e:
            logger.error(f"Error validating URL {url}: {e}")
            return False
    
    def extract_domain(self, url: str) -> str:
        """
        Extract domain from URL.
        
        Args:
            url: URL to extract domain from
            
        Returns:
            Domain string
        """
        try:
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except Exception:
            return ''
    
    def is_same_domain(self, url1: str, url2: str) -> bool:
        """
        Check if two URLs are from the same domain.
        
        Args:
            url1: First URL
            url2: Second URL
            
        Returns:
            True if same domain
        """
        return self.extract_domain(url1) == self.extract_domain(url2)
    
    def get_base_url(self, url: str) -> str:
        """
        Get base URL (scheme + netloc).
        
        Args:
            url: Full URL
            
        Returns:
            Base URL
        """
        try:
            parsed = urlparse(url)
            return f"{parsed.scheme}://{parsed.netloc}"
        except Exception:
            return url
    
    def deduplicate_urls(self, urls: list[str]) -> list[str]:
        """
        Remove duplicate URLs after normalization.
        
        Args:
            urls: List of URLs
            
        Returns:
            Deduplicated list of URLs
        """
        seen = set()
        unique_urls = []
        
        for url in urls:
            normalized = self.normalize_url(url)
            if normalized not in seen and self.is_valid_url(normalized):
                seen.add(normalized)
                unique_urls.append(normalized)
        
        return unique_urls
    
    def filter_in_scope(self, urls: list[str], scope_patterns: list[str]) -> list[str]:
        """
        Filter URLs based on scope patterns.
        
        Args:
            urls: List of URLs to filter
            scope_patterns: List of patterns that URLs must match
            
        Returns:
            Filtered list of URLs
        """
        if not scope_patterns:
            return urls
        
        filtered_urls = []
        
        for url in urls:
            for pattern in scope_patterns:
                if pattern in url:
                    filtered_urls.append(url)
                    break
        
        return filtered_urls
    
    def filter_out_scope(self, urls: list[str], exclude_patterns: list[str]) -> list[str]:
        """
        Filter out URLs based on exclude patterns.
        
        Args:
            urls: List of URLs to filter
            exclude_patterns: List of patterns that URLs must NOT match
            
        Returns:
            Filtered list of URLs
        """
        if not exclude_patterns:
            return urls
        
        filtered_urls = []
        
        for url in urls:
            should_exclude = False
            for pattern in exclude_patterns:
                if pattern in url:
                    should_exclude = True
                    break
            
            if not should_exclude:
                filtered_urls.append(url)
        
        return filtered_urls
    
    def get_url_depth(self, url: str, base_url: str) -> int:
        """
        Calculate URL depth relative to base URL.
        
        Args:
            url: URL to calculate depth for
            base_url: Base URL to calculate from
            
        Returns:
            Depth as integer
        """
        try:
            parsed_url = urlparse(url)
            parsed_base = urlparse(base_url)
            
            # Must be same domain
            if parsed_url.netloc != parsed_base.netloc:
                return -1
            
            # Count path segments
            url_segments = [seg for seg in parsed_url.path.split('/') if seg]
            base_segments = [seg for seg in parsed_base.path.split('/') if seg]
            
            return len(url_segments) - len(base_segments)
        
        except Exception:
            return 0