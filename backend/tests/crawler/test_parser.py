"""
Tests for HTML parsing and data extraction functionality.
"""

import pytest
from crawler.parser import HTMLParser


class TestHTMLParser:
    """Test cases for HTMLParser class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = HTMLParser()
        self.base_url = "http://example.com"
    
    @pytest.mark.asyncio
    async def test_basic_html_parsing(self):
        """Test basic HTML parsing functionality."""
        html = """
        <html>
            <head><title>Test Page</title></head>
            <body>
                <h1>Welcome</h1>
                <p>This is a test page.</p>
            </body>
        </html>
        """
        
        result = await self.parser.parse_html(html, self.base_url)
        
        assert isinstance(result, dict)
        assert 'links' in result
        assert 'forms' in result
        assert 'scripts' in result
        assert 'meta' in result
        assert 'title' in result
        assert result['title'] == "Test Page"
    
    @pytest.mark.asyncio
    async def test_link_extraction(self):
        """Test link extraction from HTML."""
        html = """
        <html>
            <body>
                <a href="/relative">Relative Link</a>
                <a href="http://example.com/absolute">Absolute Link</a>
                <a href="https://other.com/external">External Link</a>
                <a href="#anchor">Anchor Link</a>
                <a href="mailto:test@example.com">Email Link</a>
                <a href="javascript:void(0)">JavaScript Link</a>
            </body>
        </html>
        """
        
        result = await self.parser.parse_html(html, self.base_url)
        links = result['links']
        
        # Should extract valid HTTP/HTTPS links
        assert len(links) >= 3
        
        # Check for properly resolved relative links
        relative_found = any(link['url'] == "http://example.com/relative" for link in links)
        assert relative_found
        
        # Check for absolute links
        absolute_found = any(link['url'] == "http://example.com/absolute" for link in links)
        assert absolute_found
        
        # Check for external links
        external_found = any(link['url'] == "https://other.com/external" for link in links)
        assert external_found
    
    @pytest.mark.asyncio
    async def test_form_extraction(self):
        """Test form extraction from HTML."""
        html = """
        <html>
            <body>
                <form action="/login" method="post">
                    <input type="text" name="username" required>
                    <input type="password" name="password" required>
                    <input type="hidden" name="csrf_token" value="abc123">
                    <input type="submit" value="Login">
                </form>
                
                <form action="http://example.com/search" method="get">
                    <input type="text" name="q" placeholder="Search...">
                    <select name="category">
                        <option value="all">All</option>
                        <option value="news">News</option>
                    </select>
                    <button type="submit">Search</button>
                </form>
            </body>
        </html>
        """
        
        result = await self.parser.parse_html(html, self.base_url)
        forms = result['forms']
        
        assert len(forms) == 2
        
        # Check login form
        login_form = forms[0]
        assert login_form['action'] == "http://example.com/login"
        assert login_form['method'] == "post"
        assert len(login_form['fields']) == 4  # username, password, csrf_token, submit
        
        # Check for CSRF token detection
        csrf_fields = [f for f in login_form['fields'] if 'csrf' in f['name'].lower()]
        assert len(csrf_fields) == 1
        assert csrf_fields[0]['value'] == "abc123"
        
        # Check search form
        search_form = forms[1]
        assert search_form['action'] == "http://example.com/search"
        assert search_form['method'] == "get"
        assert len(search_form['fields']) >= 2  # q, category, submit
    
    @pytest.mark.asyncio
    async def test_script_extraction(self):
        """Test script extraction from HTML."""
        html = """
        <html>
            <head>
                <script src="/js/jquery.js"></script>
                <script src="https://cdn.example.com/bootstrap.js"></script>
                <script>
                    var config = { api_url: '/api/v1' };
                    console.log('Inline script');
                </script>
            </head>
            <body>
                <script>
                    function handleClick() {
                        alert('Button clicked');
                    }
                </script>
            </body>
        </html>
        """
        
        result = await self.parser.parse_html(html, self.base_url)
        scripts = result['scripts']
        
        # Should find both external and inline scripts
        assert len(scripts) >= 4
        
        # Check external scripts
        external_scripts = [s for s in scripts if s.get('src')]
        assert len(external_scripts) == 2
        
        # Check inline scripts
        inline_scripts = [s for s in scripts if s.get('content')]
        assert len(inline_scripts) >= 2
        
        # Verify script content extraction
        inline_content = [s['content'] for s in inline_scripts]
        assert any('config' in content for content in inline_content)
        assert any('handleClick' in content for content in inline_content)
    
    @pytest.mark.asyncio
    async def test_meta_extraction(self):
        """Test meta tag extraction from HTML."""
        html = """
        <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <meta name="description" content="Test page description">
                <meta name="keywords" content="test, html, parsing">
                <meta property="og:title" content="Test Page">
                <meta property="og:description" content="Open Graph description">
                <meta name="csrf-token" content="xyz789">
            </head>
        </html>
        """
        
        result = await self.parser.parse_html(html, self.base_url)
        meta = result['meta']
        
        assert len(meta) >= 7
        
        # Check specific meta tags
        description_meta = next((m for m in meta if m.get('name') == 'description'), None)
        assert description_meta is not None
        assert description_meta['content'] == "Test page description"
        
        # Check Open Graph tags
        og_title = next((m for m in meta if m.get('property') == 'og:title'), None)
        assert og_title is not None
        assert og_title['content'] == "Test Page"
        
        # Check CSRF token in meta
        csrf_meta = next((m for m in meta if 'csrf' in m.get('name', '').lower()), None)
        assert csrf_meta is not None
        assert csrf_meta['content'] == "xyz789"
    
    @pytest.mark.asyncio
    async def test_csrf_token_detection(self):
        """Test CSRF token detection in various forms."""
        html = """
        <html>
            <head>
                <meta name="csrf-token" content="meta-token-123">
                <meta name="_token" content="meta-token-456">
            </head>
            <body>
                <form>
                    <input type="hidden" name="csrf_token" value="form-token-789">
                    <input type="hidden" name="authenticity_token" value="auth-token-abc">
                    <input type="hidden" name="__RequestVerificationToken" value="verify-token-def">
                </form>
            </body>
        </html>
        """
        
        result = await self.parser.parse_html(html, self.base_url)
        
        # Check meta CSRF tokens
        meta_tokens = [m for m in result['meta'] if any(pattern.search(m.get('name', '')) for pattern in self.parser.csrf_regex)]
        assert len(meta_tokens) >= 2
        
        # Check form CSRF tokens
        form = result['forms'][0]
        csrf_fields = [f for f in form['fields'] if any(pattern.search(f['name']) for pattern in self.parser.csrf_regex)]
        assert len(csrf_fields) >= 3
    
    @pytest.mark.asyncio
    async def test_comment_extraction(self):
        """Test HTML comment extraction."""
        html = """
        <html>
            <!-- This is a comment -->
            <body>
                <!-- TODO: Add more content -->
                <p>Content</p>
                <!-- DEBUG: User ID = 12345 -->
            </body>
        </html>
        """
        
        result = await self.parser.parse_html(html, self.base_url)
        comments = result.get('comments', [])
        
        assert len(comments) >= 3
        assert any('This is a comment' in comment for comment in comments)
        assert any('TODO' in comment for comment in comments)
        assert any('DEBUG' in comment for comment in comments)
    
    @pytest.mark.asyncio
    async def test_image_extraction(self):
        """Test image extraction from HTML."""
        html = """
        <html>
            <body>
                <img src="/images/logo.png" alt="Logo">
                <img src="https://cdn.example.com/banner.jpg" alt="Banner">
                <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==" alt="Data URL">
            </body>
        </html>
        """
        
        result = await self.parser.parse_html(html, self.base_url)
        images = result.get('images', [])
        
        assert len(images) >= 2  # Should exclude data URLs
        
        # Check for properly resolved relative URLs
        logo_found = any(img['src'] == "http://example.com/images/logo.png" for img in images)
        assert logo_found
        
        # Check for absolute URLs
        banner_found = any(img['src'] == "https://cdn.example.com/banner.jpg" for img in images)
        assert banner_found
    
    @pytest.mark.asyncio
    async def test_malformed_html(self):
        """Test parsing of malformed HTML."""
        html = """
        <html>
            <body>
                <p>Unclosed paragraph
                <div>Nested without closing
                    <a href="/link">Link</a>
                <form action="/submit">
                    <input type="text" name="field">
                    <!-- Missing form close tag -->
            </body>
        <!-- Missing html close tag -->
        """
        
        # Should not raise an exception
        result = await self.parser.parse_html(html, self.base_url)
        
        assert isinstance(result, dict)
        assert 'links' in result
        assert 'forms' in result
        
        # Should still extract data despite malformed HTML
        assert len(result['links']) >= 1
        assert len(result['forms']) >= 1
    
    @pytest.mark.asyncio
    async def test_empty_html(self):
        """Test parsing of empty or minimal HTML."""
        # Empty string
        result = await self.parser.parse_html("", self.base_url)
        assert isinstance(result, dict)
        
        # Minimal HTML
        result = await self.parser.parse_html("<html></html>", self.base_url)
        assert isinstance(result, dict)
        assert result.get('title') == ""
        assert len(result.get('links', [])) == 0
        assert len(result.get('forms', [])) == 0
    
    @pytest.mark.asyncio
    async def test_large_html_performance(self):
        """Test parsing performance with large HTML content."""
        # Generate large HTML content
        large_html = "<html><body>"
        for i in range(1000):
            large_html += f'<a href="/page{i}">Link {i}</a>'
            large_html += f'<p>Content paragraph {i}</p>'
        large_html += "</body></html>"
        
        # Should complete within reasonable time
        import time
        start_time = time.time()
        result = await self.parser.parse_html(large_html, self.base_url)
        end_time = time.time()
        
        # Should complete within 5 seconds
        assert (end_time - start_time) < 5.0
        assert len(result['links']) == 1000