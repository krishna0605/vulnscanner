"""
Unit tests for the URL normalizer module.
Tests URL normalization, deduplication, and filtering functionality.
"""

from crawler.normalizer import URLNormalizer


class TestURLNormalizer:
    """Test cases for URLNormalizer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.normalizer = URLNormalizer()
    
    def test_basic_url_normalization(self):
        """Test basic URL normalization functionality."""
        # Test scheme normalization
        assert self.normalizer.normalize_url("HTTP://example.com") == "http://example.com/"
        assert self.normalizer.normalize_url("HTTPS://example.com") == "https://example.com/"
        
        # Test domain normalization
        assert self.normalizer.normalize_url("http://EXAMPLE.COM") == "http://example.com/"
        assert self.normalizer.normalize_url("http://Example.Com/Path") == "http://example.com/Path"
    
    def test_default_port_removal(self):
        """Test removal of default ports."""
        assert self.normalizer.normalize_url("http://example.com:80/") == "http://example.com/"
        assert self.normalizer.normalize_url("https://example.com:443/") == "https://example.com/"
        
        # Non-default ports should be preserved
        assert self.normalizer.normalize_url("http://example.com:8080/") == "http://example.com:8080/"
        assert self.normalizer.normalize_url("https://example.com:8443/") == "https://example.com:8443/"
    
    def test_path_normalization(self):
        """Test path normalization."""
        # Root path
        assert self.normalizer.normalize_url("http://example.com") == "http://example.com/"
        assert self.normalizer.normalize_url("http://example.com/") == "http://example.com/"
        
        # Trailing slash removal for non-root paths
        assert self.normalizer.normalize_url("http://example.com/path/") == "http://example.com/path"
        assert self.normalizer.normalize_url("http://example.com/path/subpath/") == "http://example.com/path/subpath"
        
        # Path without leading slash
        assert self.normalizer._normalize_path("path") == "/path"
        assert self.normalizer._normalize_path("") == "/"
    
    def test_query_parameter_normalization(self):
        """Test query parameter normalization."""
        # Parameter sorting
        url = "http://example.com/?b=2&a=1&c=3"
        normalized = self.normalizer.normalize_url(url)
        assert "a=1" in normalized
        assert "b=2" in normalized
        assert "c=3" in normalized
        
        # Empty query removal
        assert self.normalizer.normalize_url("http://example.com/?") == "http://example.com/"
    
    def test_tracking_parameter_removal(self):
        """Test removal of tracking parameters."""
        tracking_urls = [
            "http://example.com/?utm_source=google&utm_medium=cpc&page=1",
            "http://example.com/?fbclid=123456&content=test",
            "http://example.com/?gclid=abc123&_ga=xyz789&param=value"
        ]
        
        for url in tracking_urls:
            normalized = self.normalizer.normalize_url(url)
            # Tracking parameters should be removed
            assert "utm_" not in normalized
            assert "fbclid" not in normalized
            assert "gclid" not in normalized
            assert "_ga" not in normalized
            
        # Regular parameters should be preserved
        url_with_regular_param = "http://example.com/?utm_source=test&page=1&limit=10"
        normalized = self.normalizer.normalize_url(url_with_regular_param)
        assert "page=1" in normalized
        assert "limit=10" in normalized
        assert "utm_source" not in normalized
    
    def test_fragment_removal(self):
        """Test fragment removal from URLs."""
        assert self.normalizer.normalize_url("http://example.com/#section") == "http://example.com/"
        assert self.normalizer.normalize_url("http://example.com/page#anchor") == "http://example.com/page"
        assert self.normalizer.normalize_url("http://example.com/page?param=1#section") == "http://example.com/page?param=1"
    
    def test_invalid_url_handling(self):
        """Test handling of invalid URLs."""
        invalid_urls = [
            "",
            "not-a-url",
            "://example.com",
            "http://",
            "ftp://example.com"  # No scheme/netloc after parsing
        ]
        
        for url in invalid_urls:
            # Should return original URL if normalization fails
            result = self.normalizer.normalize_url(url)
            assert isinstance(result, str)
    
    def test_percent_encoding_normalization(self):
        """Test percent encoding normalization."""
        # Common characters that don't need encoding
        url = "http://example.com/path%20with%20spaces"
        normalized = self.normalizer.normalize_url(url)
        # Should handle percent encoding appropriately
        assert "example.com" in normalized
    
    def test_should_exclude_url(self):
        """Test URL exclusion based on file extensions."""
        # Image files should be excluded
        assert self.normalizer.should_exclude_url("http://example.com/image.jpg")
        assert self.normalizer.should_exclude_url("http://example.com/photo.PNG")
        assert self.normalizer.should_exclude_url("http://example.com/icon.svg")
        
        # Document files should be excluded
        assert self.normalizer.should_exclude_url("http://example.com/document.pdf")
        assert self.normalizer.should_exclude_url("http://example.com/sheet.xlsx")
        
        # Archive files should be excluded
        assert self.normalizer.should_exclude_url("http://example.com/archive.zip")
        
        # Regular web pages should not be excluded
        assert not self.normalizer.should_exclude_url("http://example.com/page.html")
        assert not self.normalizer.should_exclude_url("http://example.com/page.php")
        assert not self.normalizer.should_exclude_url("http://example.com/api/endpoint")
        assert not self.normalizer.should_exclude_url("http://example.com/")
    
    def test_is_same_domain(self):
        """Test domain comparison functionality."""
        base_url = "http://example.com"
        
        # Same domain
        assert self.normalizer.is_same_domain(base_url, "http://example.com/page")
        assert self.normalizer.is_same_domain(base_url, "https://example.com/secure")
        
        # Different domains
        assert not self.normalizer.is_same_domain(base_url, "http://other.com/page")
        assert not self.normalizer.is_same_domain(base_url, "http://sub.example.com/page")
        
        # Subdomain handling
        base_with_www = "http://www.example.com"
        assert self.normalizer.is_same_domain(base_with_www, "http://example.com/page")
        assert self.normalizer.is_same_domain("http://example.com", "http://www.example.com/page")
    
    def test_deduplication_functionality(self):
        """Test URL deduplication."""
        urls = [
            "http://example.com/",
            "http://example.com",
            "HTTP://EXAMPLE.COM/",
            "http://example.com:80/",
            "http://example.com/?utm_source=test",
            "http://example.com/#section"
        ]
        
        normalized_urls = [self.normalizer.normalize_url(url) for url in urls]
        unique_urls = list(set(normalized_urls))
        
        # All should normalize to the same URL
        assert len(unique_urls) == 1
        assert unique_urls[0] == "http://example.com/"
    
    def test_complex_url_normalization(self):
        """Test normalization of complex URLs."""
        complex_url = "HTTP://WWW.EXAMPLE.COM:80/Path/To/Page/?utm_source=google&b=2&a=1&utm_medium=cpc#section"
        expected = "https://www.example.com/Path/To/Page?a=1&b=2"
        
        normalized = self.normalizer.normalize_url(complex_url)
        assert normalized == expected
        
        # Check key components
        assert "example.com" in normalized.lower()
        assert "a=1" in normalized
        assert "b=2" in normalized
        assert "utm_" not in normalized
        assert "#section" not in normalized
    
    def test_edge_cases(self):
        """Test edge cases and error conditions."""
        # Empty string
        assert self.normalizer.normalize_url("") == ""
        
        # Whitespace
        assert self.normalizer.normalize_url("  http://example.com  ") == "http://example.com/"
        
        # Unicode characters
        unicode_url = "http://example.com/测试"
        result = self.normalizer.normalize_url(unicode_url)
        assert "example.com" in result
        
        # Very long URL
        long_path = "/very/long/path/" + "segment/" * 100
        long_url = f"http://example.com{long_path}"
        result = self.normalizer.normalize_url(long_url)
        assert "example.com" in result


class TestURLNormalizerIntegration:
    """Integration tests for URLNormalizer with realistic scenarios."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.normalizer = URLNormalizer()
    
    def test_realistic_crawling_scenario(self):
        """Test normalizer with realistic crawling URLs."""
        discovered_urls = [
            "https://example.com/",
            "https://example.com/about",
            "https://example.com/about/",
            "https://example.com/contact?utm_source=homepage",
            "https://example.com/products#featured",
            "https://example.com/blog/post-1",
            "https://example.com/images/logo.png",
            "https://example.com/docs/manual.pdf",
            "HTTPS://EXAMPLE.COM/NEWS",
            "https://example.com:443/services"
        ]
        
        # Normalize all URLs
        normalized = [self.normalizer.normalize_url(url) for url in discovered_urls]
        
        # Filter out excluded URLs
        web_pages = [url for url in normalized if not self.normalizer.should_exclude_url(url)]
        
        # Check results
        assert "https://example.com/" in web_pages
        assert "https://example.com/about" in web_pages
        assert "https://example.com/contact" in web_pages  # tracking params removed
        assert "https://example.com/blog/post-1" in web_pages
        assert "https://example.com/news" in web_pages  # case normalized
        assert "https://example.com/services" in web_pages  # default port removed
        
        # Excluded files should not be in web_pages
        excluded_count = len([url for url in normalized if self.normalizer.should_exclude_url(url)])
        assert excluded_count >= 2  # At least logo.png and manual.pdf
    
    def test_deduplication_with_variations(self):
        """Test deduplication with various URL variations."""
        url_variations = [
            "https://shop.example.com/product/123",
            "https://shop.example.com/product/123/",
            "https://shop.example.com/product/123?ref=homepage",
            "https://shop.example.com/product/123?utm_campaign=sale&color=red",
            "https://shop.example.com/product/123?color=red&utm_campaign=sale",
            "https://shop.example.com/product/123?color=red#reviews",
            "HTTPS://SHOP.EXAMPLE.COM/PRODUCT/123?COLOR=RED"
        ]
        
        normalized = [self.normalizer.normalize_url(url) for url in url_variations]
        unique_normalized = list(set(normalized))
        
        # Should deduplicate to fewer unique URLs
        assert len(unique_normalized) < len(url_variations)
        
        # All should contain the core URL structure
        for url in unique_normalized:
            assert "shop.example.com/product/123" in url
            assert "utm_" not in url  # Tracking params removed
            assert "#" not in url    # Fragments removed