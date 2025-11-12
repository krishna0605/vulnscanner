"""
Unit tests for the HTML parser module.
Tests HTML parsing, link extraction, form analysis, and data extraction functionality.
"""

import pytest
from unittest.mock import patch
from crawler.parser import HTMLParser


class TestHTMLParser:
    """Test cases for HTMLParser class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = HTMLParser()
        self.base_url = "https://example.com"
    
    @pytest.mark.asyncio
    async def test_basic_html_parsing(self):
        """Test basic HTML parsing functionality."""
        html = """
        <html>
            <head>
                <title>Test Page</title>
                <meta name="description" content="Test description">
            </head>
            <body>
                <h1>Main Heading</h1>
                <p>Test content</p>
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
        assert 'headings' in result
    
    @pytest.mark.asyncio
    async def test_link_extraction(self):
        """Test extraction of various types of links."""
        html = """
        <html>
            <body>
                <a href="/page1">Internal Link</a>
                <a href="https://external.com/page">External Link</a>
                <a href="mailto:test@example.com">Email Link</a>
                <a href="#section">Fragment Link</a>
                <a href="javascript:void(0)">JavaScript Link</a>
                <a href="relative/path">Relative Link</a>
                <area href="/map-area" alt="Map Area">
                <link rel="canonical" href="/canonical">
                <link rel="next" href="/page2">
                <link rel="stylesheet" href="/style.css">
            </body>
        </html>
        """
        
        result = await self.parser.parse_html(html, self.base_url)
        links = result['links']
        
        # Check that links are extracted
        assert len(links) > 0
        
        # Check specific links
        link_urls = [link['url'] for link in links]
        assert "https://example.com/page1" in link_urls
        assert "https://external.com/page" in link_urls
        assert "https://example.com/relative/path" in link_urls
        assert "https://example.com/map-area" in link_urls
        assert "https://example.com/canonical" in link_urls
        assert "https://example.com/page2" in link_urls
        
        # Check that fragment and javascript links are excluded
        assert not any("#section" in url for url in link_urls)
        assert not any("javascript:" in url for url in link_urls)
        
        # Check link text extraction
        link_texts = [link['text'] for link in links]
        assert "Internal Link" in link_texts
        assert "External Link" in link_texts
    
    @pytest.mark.asyncio
    async def test_form_extraction(self):
        """Test extraction of forms and their properties."""
        html = """
        <html>
            <body>
                <form action="/login" method="post">
                    <input type="text" name="username" required>
                    <input type="password" name="password" required>
                    <input type="hidden" name="csrf_token" value="abc123">
                    <input type="submit" value="Login">
                </form>
                
                <form action="/upload" method="post" enctype="multipart/form-data">
                    <input type="file" name="document">
                    <textarea name="description"></textarea>
                    <select name="category">
                        <option value="doc">Document</option>
                        <option value="img">Image</option>
                    </select>
                    <input type="submit" value="Upload">
                </form>
                
                <form>
                    <input type="email" name="email">
                    <input type="submit" value="Subscribe">
                </form>
            </body>
        </html>
        """
        
        result = await self.parser.parse_html(html, self.base_url)
        forms = result['forms']
        
        assert len(forms) == 3
        
        # Test login form
        login_form = forms[0]
        assert login_form['action'] == "https://example.com/login"
        assert login_form['method'] == "post"
        assert login_form['enctype'] == "application/x-www-form-urlencoded"
        assert len(login_form['fields']) >= 2  # username, password, submit
        assert len(login_form['csrf_tokens']) > 0
        assert len(login_form['hidden_fields']) > 0
        
        # Test upload form
        upload_form = forms[1]
        assert upload_form['action'] == "https://example.com/upload"
        assert upload_form['method'] == "post"
        assert upload_form['enctype'] == "multipart/form-data"
        assert upload_form['file_upload']
        
        # Test form without action (should default to base URL)
        subscribe_form = forms[2]
        assert subscribe_form['action'] == self.base_url
        assert subscribe_form['method'] == "get"  # default method
    
    @pytest.mark.asyncio
    async def test_csrf_token_detection(self):
        """Test detection of CSRF tokens in forms."""
        html_with_csrf = """
        <form action="/submit" method="post">
            <input type="hidden" name="csrf_token" value="token123">
            <input type="hidden" name="_token" value="token456">
            <input type="hidden" name="authenticity_token" value="token789">
            <input type="hidden" name="__RequestVerificationToken" value="tokenABC">
            <input type="text" name="data">
        </form>
        """
        
        result = await self.parser.parse_html(html_with_csrf, self.base_url)
        forms = result['forms']
        
        assert len(forms) == 1
        csrf_tokens = forms[0]['csrf_tokens']
        
        # Should detect multiple CSRF token patterns
        assert len(csrf_tokens) >= 4
        
        # Check specific token names
        token_names = [token['name'] for token in csrf_tokens]
        assert 'csrf_token' in token_names
        assert '_token' in token_names
        assert 'authenticity_token' in token_names
        assert '__RequestVerificationToken' in token_names
    
    @pytest.mark.asyncio
    async def test_script_extraction(self):
        """Test extraction of script tags and their sources."""
        html = """
        <html>
            <head>
                <script src="/js/app.js"></script>
                <script src="https://cdn.example.com/jquery.js"></script>
                <script>
                    var config = { api: '/api/v1' };
                </script>
            </head>
            <body>
                <script>
                    console.log('inline script');
                </script>
            </body>
        </html>
        """
        
        result = await self.parser.parse_html(html, self.base_url)
        scripts = result['scripts']
        
        assert len(scripts) >= 2  # At least external scripts
        
        # Check external scripts
        external_scripts = [s for s in scripts if s.get('src')]
        assert len(external_scripts) >= 2
        
        script_sources = [s['src'] for s in external_scripts]
        assert "https://example.com/js/app.js" in script_sources
        assert "https://cdn.example.com/jquery.js" in script_sources
        
        # Check inline scripts
        inline_scripts = [s for s in scripts if s.get('content')]
        assert len(inline_scripts) >= 2
    
    @pytest.mark.asyncio
    async def test_meta_tag_extraction(self):
        """Test extraction of meta tags."""
        html = """
        <html>
            <head>
                <meta name="description" content="Page description">
                <meta name="keywords" content="test, parser, html">
                <meta name="author" content="Test Author">
                <meta property="og:title" content="Open Graph Title">
                <meta http-equiv="X-Frame-Options" content="DENY">
                <meta charset="utf-8">
            </head>
        </html>
        """
        
        result = await self.parser.parse_html(html, self.base_url)
        meta_tags = result['meta']
        
        assert len(meta_tags) >= 5
        
        # Check specific meta tags
        meta_names = [tag.get('name', '') for tag in meta_tags]
        assert 'description' in meta_names
        assert 'keywords' in meta_names
        assert 'author' in meta_names
        
        # Check property-based meta tags
        meta_properties = [tag.get('property', '') for tag in meta_tags]
        assert 'og:title' in meta_properties
        
        # Check http-equiv meta tags
        meta_http_equiv = [tag.get('http-equiv', '') for tag in meta_tags]
        assert 'X-Frame-Options' in meta_http_equiv
    
    @pytest.mark.asyncio
    async def test_title_extraction(self):
        """Test title extraction."""
        html_with_title = """
        <html>
            <head>
                <title>Test Page Title</title>
            </head>
        </html>
        """
        
        result = await self.parser.parse_html(html_with_title, self.base_url)
        assert result['title'] == "Test Page Title"
        
        # Test HTML without title
        html_no_title = "<html><body>No title</body></html>"
        result = await self.parser.parse_html(html_no_title, self.base_url)
        assert result['title'] == ""
    
    @pytest.mark.asyncio
    async def test_heading_extraction(self):
        """Test extraction of heading tags."""
        html = """
        <html>
            <body>
                <h1>Main Heading</h1>
                <h2>Subheading 1</h2>
                <h2>Subheading 2</h2>
                <h3>Sub-subheading</h3>
                <h4>Level 4 Heading</h4>
                <h5>Level 5 Heading</h5>
                <h6>Level 6 Heading</h6>
            </body>
        </html>
        """
        
        result = await self.parser.parse_html(html, self.base_url)
        headings = result['headings']
        
        assert len(headings) == 7
        
        # Check heading levels
        h1_headings = [h for h in headings if h['level'] == 1]
        h2_headings = [h for h in headings if h['level'] == 2]
        
        assert len(h1_headings) == 1
        assert len(h2_headings) == 2
        assert h1_headings[0]['text'] == "Main Heading"
    
    @pytest.mark.asyncio
    async def test_comment_extraction(self):
        """Test extraction of HTML comments."""
        html = """
        <html>
            <!-- This is a comment -->
            <body>
                <!-- TODO: Add more content -->
                <p>Content</p>
                <!-- DEBUG: Remove this in production -->
            </body>
        </html>
        """
        
        result = await self.parser.parse_html(html, self.base_url)
        comments = result['comments']
        
        assert len(comments) >= 3
        
        comment_texts = [comment['text'] for comment in comments]
        assert "This is a comment" in comment_texts
        assert "TODO: Add more content" in comment_texts
        assert "DEBUG: Remove this in production" in comment_texts
    
    @pytest.mark.asyncio
    async def test_image_extraction(self):
        """Test extraction of images."""
        html = """
        <html>
            <body>
                <img src="/logo.png" alt="Logo">
                <img src="https://cdn.example.com/banner.jpg" alt="Banner">
                <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==" alt="Data URL">
            </body>
        </html>
        """
        
        result = await self.parser.parse_html(html, self.base_url)
        images = result['images']
        
        assert len(images) >= 2  # Excluding data URLs
        
        image_sources = [img['src'] for img in images]
        assert "https://example.com/logo.png" in image_sources
        assert "https://cdn.example.com/banner.jpg" in image_sources
        
        # Check alt text extraction
        image_alts = [img['alt'] for img in images]
        assert "Logo" in image_alts
        assert "Banner" in image_alts
    
    @pytest.mark.asyncio
    async def test_stylesheet_extraction(self):
        """Test extraction of stylesheets."""
        html = """
        <html>
            <head>
                <link rel="stylesheet" href="/css/main.css">
                <link rel="stylesheet" href="https://cdn.example.com/bootstrap.css">
                <style>
                    body { margin: 0; }
                </style>
            </head>
        </html>
        """
        
        result = await self.parser.parse_html(html, self.base_url)
        stylesheets = result['stylesheets']
        
        # Check external stylesheets
        external_styles = [s for s in stylesheets if s.get('href')]
        assert len(external_styles) >= 2
        
        style_hrefs = [s['href'] for s in external_styles]
        assert "https://example.com/css/main.css" in style_hrefs
        assert "https://cdn.example.com/bootstrap.css" in style_hrefs
        
        # Check inline styles
        inline_styles = [s for s in stylesheets if s.get('content')]
        assert len(inline_styles) >= 1
    
    @pytest.mark.asyncio
    async def test_input_extraction(self):
        """Test extraction of input fields."""
        html = """
        <html>
            <body>
                <input type="text" name="username" placeholder="Username">
                <input type="password" name="password" required>
                <input type="email" name="email" value="test@example.com">
                <input type="hidden" name="token" value="secret">
                <input type="checkbox" name="remember" checked>
                <input type="radio" name="gender" value="male">
                <input type="file" name="upload" accept=".pdf,.doc">
            </body>
        </html>
        """
        
        result = await self.parser.parse_html(html, self.base_url)
        inputs = result['inputs']
        
        assert len(inputs) >= 7
        
        # Check input types
        input_types = [inp['type'] for inp in inputs]
        assert 'text' in input_types
        assert 'password' in input_types
        assert 'email' in input_types
        assert 'hidden' in input_types
        assert 'checkbox' in input_types
        assert 'radio' in input_types
        assert 'file' in input_types
        
        # Check specific attributes
        email_input = next((inp for inp in inputs if inp['type'] == 'email'), None)
        assert email_input is not None
        assert email_input['value'] == 'test@example.com'
        
        file_input = next((inp for inp in inputs if inp['type'] == 'file'), None)
        assert file_input is not None
        assert file_input['accept'] == '.pdf,.doc'
    
    @pytest.mark.asyncio
    async def test_auth_form_detection(self):
        """Test detection of authentication forms."""
        login_html = """
        <form action="/login" method="post">
            <input type="text" name="username">
            <input type="password" name="password">
            <input type="submit" value="Login">
        </form>
        """
        
        result = await self.parser.parse_html(login_html, self.base_url)
        forms = result['forms']
        
        assert len(forms) == 1
        assert forms[0]['auth_required']
        
        # Test non-auth form
        contact_html = """
        <form action="/contact" method="post">
            <input type="text" name="name">
            <input type="email" name="email">
            <textarea name="message"></textarea>
            <input type="submit" value="Send">
        </form>
        """
        
        result = await self.parser.parse_html(contact_html, self.base_url)
        forms = result['forms']
        
        assert len(forms) == 1
        assert not forms[0]['auth_required']
    
    @pytest.mark.asyncio
    async def test_file_upload_detection(self):
        """Test detection of file upload forms."""
        upload_html = """
        <form action="/upload" method="post" enctype="multipart/form-data">
            <input type="file" name="document">
            <input type="submit" value="Upload">
        </form>
        """
        
        result = await self.parser.parse_html(upload_html, self.base_url)
        forms = result['forms']
        
        assert len(forms) == 1
        assert forms[0]['file_upload']
        
        # Test form without file upload
        text_html = """
        <form action="/submit" method="post">
            <input type="text" name="data">
            <input type="submit" value="Submit">
        </form>
        """
        
        result = await self.parser.parse_html(text_html, self.base_url)
        forms = result['forms']
        
        assert len(forms) == 1
        assert not forms[0]['file_upload']
    
    @pytest.mark.asyncio
    async def test_external_resource_extraction(self):
        """Test extraction of external resources."""
        html = """
        <html>
            <head>
                <script src="https://cdn.jsdelivr.net/npm/jquery@3.6.0/dist/jquery.min.js"></script>
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.1.3/css/bootstrap.min.css">
            </head>
            <body>
                <img src="https://images.unsplash.com/photo-123456">
                <iframe src="https://www.youtube.com/embed/video123"></iframe>
            </body>
        </html>
        """
        
        result = await self.parser.parse_html(html, self.base_url)
        external_resources = result['external_resources']
        
        assert len(external_resources) >= 4
        
        # Check resource types
        resource_types = [res['type'] for res in external_resources]
        assert 'script' in resource_types
        assert 'stylesheet' in resource_types
        assert 'image' in resource_types
        assert 'iframe' in resource_types
        
        # Check external domains
        resource_domains = [res['domain'] for res in external_resources]
        assert 'cdn.jsdelivr.net' in resource_domains
        assert 'cdnjs.cloudflare.com' in resource_domains
        assert 'images.unsplash.com' in resource_domains
        assert 'www.youtube.com' in resource_domains
    
    @pytest.mark.asyncio
    async def test_malformed_html_handling(self):
        """Test handling of malformed HTML."""
        malformed_html = """
        <html>
            <body>
                <div>Unclosed div
                <p>Paragraph without closing tag
                <a href="/link">Link without closing
                <form action="/submit">
                    <input type="text" name="field1"
                    <input type="submit" value="Submit">
            </body>
        """
        
        # Should not raise an exception
        result = await self.parser.parse_html(malformed_html, self.base_url)
        
        assert isinstance(result, dict)
        assert 'links' in result
        assert 'forms' in result
        
        # Should still extract some data despite malformed HTML
        assert len(result['links']) > 0
        assert len(result['forms']) > 0
    
    @pytest.mark.asyncio
    async def test_empty_html_handling(self):
        """Test handling of empty or minimal HTML."""
        empty_html = ""
        result = await self.parser.parse_html(empty_html, self.base_url)
        
        assert isinstance(result, dict)
        assert result['links'] == []
        assert result['forms'] == []
        assert result['title'] == ""
        
        minimal_html = "<html></html>"
        result = await self.parser.parse_html(minimal_html, self.base_url)
        
        assert isinstance(result, dict)
        assert result['links'] == []
        assert result['forms'] == []
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling in parsing."""
        # Test with None input
        with patch('crawler.parser.logger') as mock_logger:
            result = await self.parser.parse_html(None, self.base_url)
            assert result == {}
            mock_logger.error.assert_called()
    
    def test_csrf_pattern_compilation(self):
        """Test CSRF pattern compilation."""
        parser = HTMLParser()
        
        assert len(parser.csrf_patterns) > 0
        assert len(parser.csrf_regex) == len(parser.csrf_patterns)
        
        # Test pattern matching
        test_names = [
            'csrf_token',
            '_token',
            'authenticity_token',
            '__RequestVerificationToken',
            'csrfmiddlewaretoken',
            'CSRF_TOKEN',  # Case insensitive
            'csrf-token'   # Dash variant
        ]
        
        for name in test_names:
            matches = any(pattern.search(name) for pattern in parser.csrf_regex)
            assert matches, f"Pattern should match {name}"


class TestHTMLParserIntegration:
    """Integration tests for HTMLParser with realistic scenarios."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = HTMLParser()
        self.base_url = "https://example.com"
    
    @pytest.mark.asyncio
    async def test_realistic_webpage_parsing(self):
        """Test parsing of a realistic webpage."""
        realistic_html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Example Website - Home</title>
            <meta name="description" content="Welcome to our example website">
            <link rel="stylesheet" href="/css/main.css">
            <link rel="canonical" href="https://example.com/">
            <script src="/js/analytics.js"></script>
        </head>
        <body>
            <header>
                <nav>
                    <a href="/">Home</a>
                    <a href="/about">About</a>
                    <a href="/products">Products</a>
                    <a href="/contact">Contact</a>
                </nav>
            </header>
            
            <main>
                <h1>Welcome to Example.com</h1>
                <p>This is our homepage content.</p>
                
                <form action="/newsletter" method="post">
                    <input type="email" name="email" placeholder="Enter your email" required>
                    <input type="hidden" name="csrf_token" value="abc123xyz">
                    <input type="submit" value="Subscribe">
                </form>
                
                <section>
                    <h2>Latest Products</h2>
                    <div>
                        <a href="/products/widget-1">
                            <img src="/images/widget1.jpg" alt="Widget 1">
                            <h3>Amazing Widget</h3>
                        </a>
                    </div>
                </section>
            </main>
            
            <footer>
                <p>&copy; 2024 Example.com</p>
                <a href="/privacy">Privacy Policy</a>
                <a href="/terms">Terms of Service</a>
            </footer>
            
            <script>
                // Analytics code
                gtag('config', 'GA-XXXXX-X');
            </script>
        </body>
        </html>
        """
        
        result = await self.parser.parse_html(realistic_html, self.base_url)
        
        # Verify comprehensive data extraction
        assert result['title'] == "Example Website - Home"
        assert len(result['links']) >= 7  # Navigation + product + footer links
        assert len(result['forms']) == 1
        assert len(result['images']) >= 1
        assert len(result['scripts']) >= 2  # External + inline
        assert len(result['stylesheets']) >= 1
        assert len(result['headings']) >= 3  # h1, h2, h3
        assert len(result['meta']) >= 3
        
        # Verify form analysis
        form = result['forms'][0]
        assert form['action'] == "https://example.com/newsletter"
        assert form['method'] == "post"
        assert len(form['csrf_tokens']) > 0
        assert form['csrf_tokens'][0]['name'] == 'csrf_token'
        
        # Verify link extraction
        link_urls = [link['url'] for link in result['links']]
        assert "https://example.com/about" in link_urls
        assert "https://example.com/products" in link_urls
        assert "https://example.com/contact" in link_urls
        assert "https://example.com/products/widget-1" in link_urls