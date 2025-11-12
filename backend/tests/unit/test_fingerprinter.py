"""
Unit tests for the technology fingerprinter module.
Tests technology detection, security header analysis, and fingerprinting functionality.
"""

import pytest
from crawler.fingerprinter import TechnologyFingerprinter


class TestTechnologyFingerprinter:
    """Test cases for TechnologyFingerprinter class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.fingerprinter = TechnologyFingerprinter()
    
    def test_signature_loading(self):
        """Test that technology signatures are loaded correctly."""
        signatures = self.fingerprinter.technology_signatures
        
        assert isinstance(signatures, dict)
        assert len(signatures) > 0
        
        # Check for key technology categories
        categories = set()
        for tech_info in signatures.values():
            categories.add(tech_info['category'])
        
        expected_categories = {
            'web_server', 'language', 'framework', 'cms', 
            'javascript', 'css_framework', 'analytics', 'cdn'
        }
        assert expected_categories.issubset(categories)
        
        # Check specific technologies
        assert 'apache' in signatures
        assert 'nginx' in signatures
        assert 'php' in signatures
        assert 'wordpress' in signatures
        assert 'jquery' in signatures
    
    def test_security_headers_list(self):
        """Test that security headers list is comprehensive."""
        headers = self.fingerprinter.security_headers
        
        assert isinstance(headers, list)
        assert len(headers) > 0
        
        # Check for important security headers
        expected_headers = [
            'strict-transport-security',
            'content-security-policy',
            'x-frame-options',
            'x-content-type-options',
            'x-xss-protection'
        ]
        
        for header in expected_headers:
            assert header in headers
    
    @pytest.mark.asyncio
    async def test_apache_detection_from_headers(self):
        """Test detection of Apache web server from headers."""
        response_data = {
            'url': 'https://example.com',
            'status_code': 200,
            'headers': {
                'Server': 'Apache/2.4.41 (Ubuntu)'
            },
            'content': '<html><body>Test</body></html>'
        }
        
        result = await self.fingerprinter.analyze_response(response_data)
        
        assert result['server_software'] == 'apache/2.4.41 (ubuntu)'
        assert 'apache' in [tech['name'] for tech in result['technologies']]
        
        # Check technology categorization
        apache_tech = next(tech for tech in result['technologies'] if tech['name'] == 'apache')
        assert apache_tech['category'] == 'web_server'
    
    @pytest.mark.asyncio
    async def test_nginx_detection_from_headers(self):
        """Test detection of Nginx web server from headers."""
        response_data = {
            'url': 'https://example.com',
            'status_code': 200,
            'headers': {
                'Server': 'nginx/1.18.0'
            },
            'content': ''
        }
        
        result = await self.fingerprinter.analyze_response(response_data)
        
        assert result['server_software'] == 'nginx/1.18.0'
        assert 'nginx' in [tech['name'] for tech in result['technologies']]
    
    @pytest.mark.asyncio
    async def test_php_detection_from_headers(self):
        """Test detection of PHP from headers."""
        response_data = {
            'url': 'https://example.com',
            'status_code': 200,
            'headers': {
                'X-Powered-By': 'PHP/8.1.0'
            },
            'content': ''
        }
        
        result = await self.fingerprinter.analyze_response(response_data)
        
        assert 'php' in [tech['name'] for tech in result['technologies']]
        
        php_tech = next(tech for tech in result['technologies'] if tech['name'] == 'php')
        assert php_tech['category'] == 'language'
    
    @pytest.mark.asyncio
    async def test_aspnet_detection_from_headers(self):
        """Test detection of ASP.NET from headers."""
        response_data = {
            'url': 'https://example.com',
            'status_code': 200,
            'headers': {
                'X-Powered-By': 'ASP.NET',
                'X-AspNet-Version': '4.0.30319'
            },
            'content': ''
        }
        
        result = await self.fingerprinter.analyze_response(response_data)
        
        assert 'asp.net' in [tech['name'] for tech in result['technologies']]
    
    @pytest.mark.asyncio
    async def test_nodejs_detection_from_headers(self):
        """Test detection of Node.js from headers."""
        response_data = {
            'url': 'https://example.com',
            'status_code': 200,
            'headers': {
                'X-Powered-By': 'Express'
            },
            'content': ''
        }
        
        result = await self.fingerprinter.analyze_response(response_data)
        
        tech_names = [tech['name'] for tech in result['technologies']]
        assert 'nodejs' in tech_names or 'express' in tech_names
    
    @pytest.mark.asyncio
    async def test_wordpress_detection_from_html(self):
        """Test detection of WordPress from HTML content."""
        html_content = """
        <html>
        <head>
            <link rel="stylesheet" href="/wp-content/themes/theme/style.css">
            <script src="/wp-includes/js/jquery/jquery.js"></script>
        </head>
        <body>
            <div class="wp-content">
                <a href="/wp-admin/">Admin</a>
            </div>
        </body>
        </html>
        """
        
        response_data = {
            'url': 'https://example.com',
            'status_code': 200,
            'headers': {},
            'content': html_content
        }
        
        result = await self.fingerprinter.analyze_response(response_data)
        
        assert 'wordpress' in [tech['name'] for tech in result['technologies']]
        
        wp_tech = next(tech for tech in result['technologies'] if tech['name'] == 'wordpress')
        assert wp_tech['category'] == 'cms'
    
    @pytest.mark.asyncio
    async def test_drupal_detection_from_html(self):
        """Test detection of Drupal from HTML content."""
        html_content = """
        <html>
        <head>
            <script src="/sites/default/files/js/drupal.js"></script>
        </head>
        <body>
            <div id="drupal-content">
                <script src="/sites/all/modules/custom/script.js"></script>
            </div>
        </body>
        </html>
        """
        
        response_data = {
            'url': 'https://example.com',
            'status_code': 200,
            'headers': {},
            'content': html_content
        }
        
        result = await self.fingerprinter.analyze_response(response_data)
        
        assert 'drupal' in [tech['name'] for tech in result['technologies']]
    
    @pytest.mark.asyncio
    async def test_jquery_detection_from_html(self):
        """Test detection of jQuery from HTML content."""
        html_content = """
        <html>
        <head>
            <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        </head>
        <body>
            <script>
                $(document).ready(function() {
                    console.log('jQuery loaded');
                });
            </script>
        </body>
        </html>
        """
        
        response_data = {
            'url': 'https://example.com',
            'status_code': 200,
            'headers': {},
            'content': html_content
        }
        
        result = await self.fingerprinter.analyze_response(response_data)
        
        assert 'jquery' in [tech['name'] for tech in result['technologies']]
        assert len(result['javascript_libraries']) > 0
    
    @pytest.mark.asyncio
    async def test_react_detection_from_html(self):
        """Test detection of React from HTML content."""
        html_content = """
        <html>
        <head>
            <script src="/static/js/react.min.js"></script>
        </head>
        <body>
            <div id="react-root"></div>
            <script>
                ReactDOM.render(React.createElement('div'), document.getElementById('react-root'));
            </script>
        </body>
        </html>
        """
        
        response_data = {
            'url': 'https://example.com',
            'status_code': 200,
            'headers': {},
            'content': html_content
        }
        
        result = await self.fingerprinter.analyze_response(response_data)
        
        assert 'react' in [tech['name'] for tech in result['technologies']]
    
    @pytest.mark.asyncio
    async def test_bootstrap_detection_from_html(self):
        """Test detection of Bootstrap from HTML content."""
        html_content = """
        <html>
        <head>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css">
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        </head>
        <body>
            <div class="container">
                <div class="row">
                    <div class="col-md-6">Bootstrap content</div>
                </div>
            </div>
        </body>
        </html>
        """
        
        response_data = {
            'url': 'https://example.com',
            'status_code': 200,
            'headers': {},
            'content': html_content
        }
        
        result = await self.fingerprinter.analyze_response(response_data)
        
        assert 'bootstrap' in [tech['name'] for tech in result['technologies']]
        assert len(result['css_frameworks']) > 0
    
    @pytest.mark.asyncio
    async def test_google_analytics_detection(self):
        """Test detection of Google Analytics from HTML content."""
        html_content = """
        <html>
        <head>
            <script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
            <script>
                window.dataLayer = window.dataLayer || [];
                function gtag(){dataLayer.push(arguments);}
                gtag('js', new Date());
                gtag('config', 'GA_MEASUREMENT_ID');
            </script>
        </head>
        <body>
            <p>Content with Google Analytics</p>
        </body>
        </html>
        """
        
        response_data = {
            'url': 'https://example.com',
            'status_code': 200,
            'headers': {},
            'content': html_content
        }
        
        result = await self.fingerprinter.analyze_response(response_data)
        
        assert 'google_analytics' in [tech['name'] for tech in result['technologies']]
        assert len(result['analytics']) > 0
    
    @pytest.mark.asyncio
    async def test_security_headers_analysis(self):
        """Test analysis of security headers."""
        response_data = {
            'url': 'https://example.com',
            'status_code': 200,
            'headers': {
                'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
                'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'",
                'X-Frame-Options': 'DENY',
                'X-Content-Type-Options': 'nosniff',
                'X-XSS-Protection': '1; mode=block',
                'Referrer-Policy': 'strict-origin-when-cross-origin'
            },
            'content': ''
        }
        
        result = await self.fingerprinter.analyze_response(response_data)
        
        security_headers = result['security_headers']
        
        assert 'strict-transport-security' in security_headers
        assert 'content-security-policy' in security_headers
        assert 'x-frame-options' in security_headers
        assert 'x-content-type-options' in security_headers
        assert 'x-xss-protection' in security_headers
        assert 'referrer-policy' in security_headers
        
        # Check header values
        assert security_headers['strict-transport-security'] == 'max-age=31536000; includeSubDomains'
        assert security_headers['x-frame-options'] == 'DENY'
    
    @pytest.mark.asyncio
    async def test_cloudflare_detection(self):
        """Test detection of Cloudflare CDN."""
        response_data = {
            'url': 'https://example.com',
            'status_code': 200,
            'headers': {
                'Server': 'cloudflare',
                'CF-Ray': '6a1b2c3d4e5f6789-LAX'
            },
            'content': ''
        }
        
        result = await self.fingerprinter.analyze_response(response_data)
        
        assert 'cloudflare' in [tech['name'] for tech in result['technologies']]
        assert result['cdn'] == 'cloudflare'
    
    @pytest.mark.asyncio
    async def test_django_detection_from_html(self):
        """Test detection of Django framework from HTML patterns."""
        html_content = """
        <html>
        <body>
            <form method="post">
                <input type="hidden" name="csrfmiddlewaretoken" value="abc123xyz">
                <input type="text" name="username">
                <input type="submit" value="Submit">
            </form>
        </body>
        </html>
        """
        
        response_data = {
            'url': 'https://example.com',
            'status_code': 200,
            'headers': {},
            'content': html_content
        }
        
        result = await self.fingerprinter.analyze_response(response_data)
        
        assert 'django' in [tech['name'] for tech in result['technologies']]
        assert result['framework'] == 'django'
    
    @pytest.mark.asyncio
    async def test_laravel_detection_from_html(self):
        """Test detection of Laravel framework from HTML patterns."""
        html_content = """
        <html>
        <body>
            <form method="post">
                <input type="hidden" name="_token" value="laravel_csrf_token">
                <input type="text" name="email">
                <input type="submit" value="Submit">
            </form>
            <script>
                // Laravel session data
                window.Laravel = {"csrfToken":"token123"};
            </script>
        </body>
        </html>
        """
        
        response_data = {
            'url': 'https://example.com',
            'status_code': 200,
            'headers': {},
            'content': html_content
        }
        
        result = await self.fingerprinter.analyze_response(response_data)
        
        assert 'laravel' in [tech['name'] for tech in result['technologies']]
    
    @pytest.mark.asyncio
    async def test_multiple_technologies_detection(self):
        """Test detection of multiple technologies in one response."""
        html_content = """
        <html>
        <head>
            <link rel="stylesheet" href="/wp-content/themes/theme/style.css">
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css">
            <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
            <script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
        </head>
        <body>
            <div class="container">
                <div class="wp-content">
                    <p>WordPress site with Bootstrap and jQuery</p>
                </div>
            </div>
            <script>
                gtag('config', 'GA_MEASUREMENT_ID');
            </script>
        </body>
        </html>
        """
        
        response_data = {
            'url': 'https://example.com',
            'status_code': 200,
            'headers': {
                'Server': 'Apache/2.4.41',
                'X-Powered-By': 'PHP/8.1.0'
            },
            'content': html_content
        }
        
        result = await self.fingerprinter.analyze_response(response_data)
        
        tech_names = [tech['name'] for tech in result['technologies']]
        
        # Should detect multiple technologies
        assert 'apache' in tech_names
        assert 'php' in tech_names
        assert 'wordpress' in tech_names
        assert 'bootstrap' in tech_names
        assert 'jquery' in tech_names
        assert 'google_analytics' in tech_names
        
        # Check categorization
        assert result['cms'] == 'wordpress'
        assert len(result['javascript_libraries']) > 0
        assert len(result['css_frameworks']) > 0
        assert len(result['analytics']) > 0
    
    @pytest.mark.asyncio
    async def test_case_insensitive_detection(self):
        """Test that detection is case insensitive."""
        response_data = {
            'url': 'https://example.com',
            'status_code': 200,
            'headers': {
                'SERVER': 'APACHE/2.4.41',
                'x-powered-by': 'php/8.1.0'
            },
            'content': ''
        }
        
        result = await self.fingerprinter.analyze_response(response_data)
        
        tech_names = [tech['name'] for tech in result['technologies']]
        assert 'apache' in tech_names
        assert 'php' in tech_names
    
    @pytest.mark.asyncio
    async def test_empty_response_handling(self):
        """Test handling of empty response data."""
        response_data = {
            'url': 'https://example.com',
            'status_code': 200,
            'headers': {},
            'content': ''
        }
        
        result = await self.fingerprinter.analyze_response(response_data)
        
        assert isinstance(result, dict)
        assert result['url'] == 'https://example.com'
        assert result['status_code'] == 200
        assert result['technologies'] == []
        assert result['security_headers'] == {}
    
    @pytest.mark.asyncio
    async def test_malformed_html_handling(self):
        """Test handling of malformed HTML content."""
        malformed_html = """
        <html>
            <head>
                <script src="/wp-content/themes/theme/script.js"
                <link rel="stylesheet" href="bootstrap.css">
            </head>
            <body>
                <div class="container">
                    <p>Malformed HTML with unclosed tags
        """
        
        response_data = {
            'url': 'https://example.com',
            'status_code': 200,
            'headers': {},
            'content': malformed_html
        }
        
        # Should not raise an exception
        result = await self.fingerprinter.analyze_response(response_data)
        
        assert isinstance(result, dict)
        # Should still detect some technologies despite malformed HTML
        tech_names = [tech['name'] for tech in result['technologies']]
        assert 'wordpress' in tech_names or 'bootstrap' in tech_names
    
    @pytest.mark.asyncio
    async def test_missing_content_handling(self):
        """Test handling when content is missing from response data."""
        response_data = {
            'url': 'https://example.com',
            'status_code': 200,
            'headers': {
                'Server': 'nginx/1.18.0'
            }
            # No 'content' key
        }
        
        result = await self.fingerprinter.analyze_response(response_data)
        
        assert isinstance(result, dict)
        assert 'nginx' in [tech['name'] for tech in result['technologies']]
    
    def test_add_technology_method(self):
        """Test the _add_technology helper method."""
        fingerprint = {
            'server_software': None,
            'programming_language': None,
            'framework': None,
            'cms': None,
            'javascript_libraries': [],
            'css_frameworks': [],
            'analytics': [],
            'technologies': [],
            'cdn': None
        }
        
        # Test adding web server
        self.fingerprinter._add_technology(fingerprint, 'apache', 'web_server')
        assert fingerprint['server_software'] == 'apache'
        assert len(fingerprint['technologies']) == 1
        assert fingerprint['technologies'][0]['name'] == 'apache'
        assert fingerprint['technologies'][0]['category'] == 'web_server'
        
        # Test adding programming language
        self.fingerprinter._add_technology(fingerprint, 'php', 'language')
        assert fingerprint['programming_language'] == 'php'
        
        # Test adding framework
        self.fingerprinter._add_technology(fingerprint, 'django', 'framework')
        assert fingerprint['framework'] == 'django'
        
        # Test adding CMS
        self.fingerprinter._add_technology(fingerprint, 'wordpress', 'cms')
        assert fingerprint['cms'] == 'wordpress'
        
        # Test adding JavaScript library
        self.fingerprinter._add_technology(fingerprint, 'jquery', 'javascript')
        assert 'jquery' in fingerprint['javascript_libraries']
        
        # Test adding CSS framework
        self.fingerprinter._add_technology(fingerprint, 'bootstrap', 'css_framework')
        assert 'bootstrap' in fingerprint['css_frameworks']
        
        # Test adding analytics
        self.fingerprinter._add_technology(fingerprint, 'google_analytics', 'analytics')
        assert 'google_analytics' in fingerprint['analytics']
        
        # Test adding CDN
        self.fingerprinter._add_technology(fingerprint, 'cloudflare', 'cdn')
        assert fingerprint['cdn'] == 'cloudflare'


class TestTechnologyFingerprinterIntegration:
    """Integration tests for TechnologyFingerprinter with realistic scenarios."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.fingerprinter = TechnologyFingerprinter()
    
    @pytest.mark.asyncio
    async def test_wordpress_site_fingerprinting(self):
        """Test fingerprinting of a typical WordPress site."""
        response_data = {
            'url': 'https://blog.example.com',
            'status_code': 200,
            'headers': {
                'Server': 'Apache/2.4.41 (Ubuntu)',
                'X-Powered-By': 'PHP/8.1.0',
                'Content-Type': 'text/html; charset=UTF-8'
            },
            'content': """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>My WordPress Blog</title>
                <link rel="stylesheet" href="/wp-content/themes/twentytwentyone/style.css">
                <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css">
                <script src="/wp-includes/js/jquery/jquery.min.js"></script>
                <script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
            </head>
            <body class="home blog">
                <div class="wp-site-blocks">
                    <header class="wp-block-template-part">
                        <nav class="wp-block-navigation">
                            <a href="/wp-admin/">Dashboard</a>
                        </nav>
                    </header>
                    <main class="wp-block-group">
                        <article class="wp-block-post">
                            <h1>Welcome to WordPress</h1>
                            <div class="wp-block-post-content">
                                <p>This is a WordPress blog post.</p>
                            </div>
                        </article>
                    </main>
                </div>
                <script>
                    gtag('config', 'GA_MEASUREMENT_ID');
                </script>
            </body>
            </html>
            """
        }
        
        result = await self.fingerprinter.analyze_response(response_data)
        
        # Verify comprehensive detection
        tech_names = [tech['name'] for tech in result['technologies']]
        
        assert 'apache' in tech_names
        assert 'php' in tech_names
        assert 'wordpress' in tech_names
        assert 'bootstrap' in tech_names
        assert 'jquery' in tech_names
        assert 'google_analytics' in tech_names
        
        # Verify categorization
        assert result['server_software'] == 'apache/2.4.41 (ubuntu)'
        assert result['programming_language'] == 'php'
        assert result['cms'] == 'wordpress'
        assert 'jquery' in result['javascript_libraries']
        assert 'bootstrap' in result['css_frameworks']
        assert 'google_analytics' in result['analytics']
    
    @pytest.mark.asyncio
    async def test_react_spa_fingerprinting(self):
        """Test fingerprinting of a React single-page application."""
        response_data = {
            'url': 'https://app.example.com',
            'status_code': 200,
            'headers': {
                'Server': 'nginx/1.18.0',
                'X-Powered-By': 'Express',
                'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'",
                'X-Frame-Options': 'SAMEORIGIN'
            },
            'content': """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="utf-8">
                <title>React App</title>
                <link rel="stylesheet" href="/static/css/bootstrap.min.css">
            </head>
            <body>
                <div id="root"></div>
                <script src="/static/js/react.min.js"></script>
                <script src="/static/js/react-dom.min.js"></script>
                <script>
                    ReactDOM.render(
                        React.createElement('div', null, 'Hello React!'),
                        document.getElementById('root')
                    );
                </script>
            </body>
            </html>
            """
        }
        
        result = await self.fingerprinter.analyze_response(response_data)
        
        tech_names = [tech['name'] for tech in result['technologies']]
        
        assert 'nginx' in tech_names
        assert 'nodejs' in tech_names or 'express' in tech_names
        assert 'react' in tech_names
        assert 'bootstrap' in tech_names
        
        # Verify security headers
        assert 'content-security-policy' in result['security_headers']
        assert 'x-frame-options' in result['security_headers']
    
    @pytest.mark.asyncio
    async def test_ecommerce_site_fingerprinting(self):
        """Test fingerprinting of an e-commerce site with multiple technologies."""
        response_data = {
            'url': 'https://shop.example.com',
            'status_code': 200,
            'headers': {
                'Server': 'Apache/2.4.41',
                'X-Powered-By': 'PHP/8.1.0',
                'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
                'Content-Security-Policy': "default-src 'self'",
                'X-Content-Type-Options': 'nosniff'
            },
            'content': """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Online Shop</title>
                <link rel="stylesheet" href="/skin/frontend/default/theme/css/styles.css">
                <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css">
                <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
                <script src="/js/mage/cookies.js"></script>
                <script>
                    // Facebook Pixel
                    fbq('track', 'PageView');
                </script>
            </head>
            <body>
                <div class="page-wrapper">
                    <div class="header-container">
                        <div class="header">
                            <a href="/customer/account/">My Account</a>
                            <a href="/checkout/cart/">Cart</a>
                        </div>
                    </div>
                    <div class="main-container">
                        <div class="col-main">
                            <div class="category-products">
                                <div class="products-grid">
                                    <div class="item">Product 1</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <script src="/var/connect/skin/adminhtml/default/default/lib/prototype/prototype.js"></script>
            </body>
            </html>
            """
        }
        
        result = await self.fingerprinter.analyze_response(response_data)
        
        tech_names = [tech['name'] for tech in result['technologies']]
        
        assert 'apache' in tech_names
        assert 'php' in tech_names
        assert 'magento' in tech_names
        assert 'bootstrap' in tech_names
        assert 'jquery' in tech_names
        assert 'facebook_pixel' in tech_names
        
        # Verify security headers
        security_headers = result['security_headers']
        assert 'strict-transport-security' in security_headers
        assert 'content-security-policy' in security_headers
        assert 'x-content-type-options' in security_headers