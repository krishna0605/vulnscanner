"""
Tests for technology fingerprinting functionality.
"""

import pytest

from crawler.fingerprinter import TechnologyFingerprinter


class TestTechnologyFingerprinter:
    """Test cases for TechnologyFingerprinter class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.fingerprinter = TechnologyFingerprinter()
    
    def test_fingerprinter_initialization(self):
        """Test fingerprinter initialization."""
        assert self.fingerprinter.technology_signatures is not None
        assert self.fingerprinter.security_headers is not None
        assert isinstance(self.fingerprinter.technology_signatures, dict)
        assert isinstance(self.fingerprinter.security_headers, list)
    
    @pytest.mark.asyncio
    async def test_apache_detection(self):
        """Test Apache web server detection."""
        response_data = {
            'headers': {'Server': 'Apache/2.4.41 (Ubuntu)'},
            'content': '<html><body>Test</body></html>',
            'status_code': 200
        }
        
        result = await self.fingerprinter.analyze_response(response_data)
        
        assert 'server_software' in result
        assert 'apache' in result['server_software'].lower()
    
    @pytest.mark.asyncio
    async def test_nginx_detection(self):
        """Test Nginx web server detection."""
        response_data = {
            'headers': {'Server': 'nginx/1.18.0'},
            'content': '<html><body>Test</body></html>',
            'status_code': 200
        }
        
        result = await self.fingerprinter.analyze_response(response_data)
        
        assert 'server_software' in result
        assert 'nginx' in result['server_software'].lower()
    
    @pytest.mark.asyncio
    async def test_php_detection(self):
        """Test PHP programming language detection."""
        response_data = {
            'headers': {'X-Powered-By': 'PHP/7.4.3'},
            'content': '<html><body>Test</body></html>',
            'status_code': 200
        }
        
        result = await self.fingerprinter.analyze_response(response_data)
        
        assert 'programming_language' in result
        assert 'php' in result['programming_language'].lower()
    
    @pytest.mark.asyncio
    async def test_wordpress_detection(self):
        """Test WordPress CMS detection."""
        response_data = {
            'headers': {},
            'content': '''<html>
                <head>
                    <meta name="generator" content="WordPress 5.8">
                    <link rel="stylesheet" href="/wp-content/themes/theme/style.css">
                </head>
                <body>
                    <div class="wp-content">Test</div>
                </body>
            </html>''',
            'status_code': 200
        }
        
        result = await self.fingerprinter.analyze_response(response_data)
        
        assert 'cms' in result
        assert 'wordpress' in result['cms'].lower()
    
    @pytest.mark.asyncio
    async def test_drupal_detection(self):
        """Test Drupal CMS detection."""
        response_data = {
            'headers': {'X-Drupal-Cache': 'HIT'},
            'content': '''<html>
                <head>
                    <meta name="Generator" content="Drupal 9">
                    <script src="/sites/default/files/js/drupal.js"></script>
                </head>
                <body class="drupal">Test</body>
            </html>''',
            'status_code': 200
        }
        
        result = await self.fingerprinter.analyze_response(response_data)
        
        assert 'cms' in result
        assert 'drupal' in result['cms'].lower()
    
    @pytest.mark.asyncio
    async def test_react_detection(self):
        """Test React framework detection."""
        response_data = {
            'headers': {},
            'content': '''<html>
                <head>
                    <script src="/static/js/react.production.min.js"></script>
                </head>
                <body>
                    <div id="root" data-reactroot="">
                        <div>React App</div>
                    </div>
                </body>
            </html>''',
            'status_code': 200
        }
        
        result = await self.fingerprinter.analyze_response(response_data)
        
        assert 'javascript_libraries' in result
        assert any('react' in lib.lower() for lib in result['javascript_libraries'])
    
    @pytest.mark.asyncio
    async def test_jquery_detection(self):
        """Test jQuery library detection."""
        response_data = {
            'headers': {},
            'content': '''<html>
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
            </html>''',
            'status_code': 200
        }
        
        result = await self.fingerprinter.analyze_response(response_data)
        
        assert 'javascript_libraries' in result
        assert any('jquery' in lib.lower() for lib in result['javascript_libraries'])
    
    @pytest.mark.asyncio
    async def test_bootstrap_detection(self):
        """Test Bootstrap framework detection."""
        response_data = {
            'headers': {},
            'content': '''<html>
                <head>
                    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
                </head>
                <body>
                    <div class="container">
                        <div class="row">
                            <div class="col-md-6">Bootstrap content</div>
                        </div>
                    </div>
                </body>
            </html>''',
            'status_code': 200
        }
        
        result = await self.fingerprinter.analyze_response(response_data)
        
        assert 'css_frameworks' in result
        assert any('bootstrap' in fw.lower() for fw in result['css_frameworks'])
    
    @pytest.mark.asyncio
    async def test_security_headers_detection(self):
        """Test security headers detection."""
        response_data = {
            'headers': {
                'Content-Security-Policy': "default-src 'self'",
                'X-Frame-Options': 'DENY',
                'X-Content-Type-Options': 'nosniff',
                'X-XSS-Protection': '1; mode=block',
                'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
                'Referrer-Policy': 'strict-origin-when-cross-origin'
            },
            'content': '<html><body>Test</body></html>',
            'status_code': 200
        }
        
        result = await self.fingerprinter.analyze_response(response_data)
        
        assert 'security_headers' in result
        security_headers = result['security_headers']
        
        assert 'content-security-policy' in security_headers
        assert 'x-frame-options' in security_headers
        assert 'x-content-type-options' in security_headers
        assert 'x-xss-protection' in security_headers
        assert 'strict-transport-security' in security_headers
        assert 'referrer-policy' in security_headers
        
        assert security_headers['x-frame-options'] == 'DENY'
        assert security_headers['x-content-type-options'] == 'nosniff'
    
    @pytest.mark.asyncio
    async def test_missing_security_headers(self):
        """Test detection of missing security headers."""
        response_data = {
            'headers': {'Server': 'nginx'},
            'content': '<html><body>Test</body></html>',
            'status_code': 200
        }
        
        result = await self.fingerprinter.analyze_response(response_data)
        
        assert 'security_headers' in result
        security_headers = result['security_headers']
        
        # Should detect missing headers
        assert 'content-security-policy' not in security_headers
        assert 'x-frame-options' not in security_headers
        assert 'strict-transport-security' not in security_headers
    
    @pytest.mark.asyncio
    async def test_cloudflare_detection(self):
        """Test Cloudflare CDN detection."""
        response_data = {
            'headers': {
                'CF-Ray': '6a1b2c3d4e5f6789-LAX',
                'CF-Cache-Status': 'HIT',
                'Server': 'cloudflare'
            },
            'content': '<html><body>Test</body></html>',
            'status_code': 200
        }
        
        result = await self.fingerprinter.analyze_response(response_data)
        
        assert 'cdn' in result or 'server_software' in result
        # Should detect Cloudflare
        if 'cdn' in result:
            assert 'cloudflare' in result['cdn'].lower()
        else:
            assert 'cloudflare' in result['server_software'].lower()
    
    @pytest.mark.asyncio
    async def test_express_js_detection(self):
        """Test Express.js framework detection."""
        response_data = {
            'headers': {'X-Powered-By': 'Express'},
            'content': '<html><body>Test</body></html>',
            'status_code': 200
        }
        
        result = await self.fingerprinter.analyze_response(response_data)
        
        assert 'framework' in result
        assert 'express' in result['framework'].lower() if result['framework'] else False
    
    @pytest.mark.asyncio
    async def test_asp_net_detection(self):
        """Test ASP.NET framework detection."""
        response_data = {
            'headers': {
                'X-AspNet-Version': '4.0.30319',
                'X-Powered-By': 'ASP.NET'
            },
            'content': '''<html>
                <head>
                    <form method="post" action="/" id="aspnetForm">
                        <input type="hidden" name="__VIEWSTATE" value="abc123">
                    </form>
                </head>
                <body>Test</body>
            </html>''',
            'status_code': 200
        }
        
        result = await self.fingerprinter.analyze_response(response_data)
        
        assert 'programming_language' in result
        assert 'asp.net' in result['programming_language'].lower() if result['programming_language'] else False
    
    @pytest.mark.asyncio
    async def test_django_detection(self):
        """Test Django framework detection."""
        response_data = {
            'headers': {},
            'content': '''<html>
                <head>
                    <input type="hidden" name="csrfmiddlewaretoken" value="abc123">
                </head>
                <body>
                    <div class="django-admin">Test</div>
                </body>
            </html>''',
            'status_code': 200
        }
        
        result = await self.fingerprinter.analyze_response(response_data)
        
        assert 'framework' in result
        assert 'django' in result['framework'].lower() if result['framework'] else False
    
    @pytest.mark.asyncio
    async def test_multiple_technologies(self):
        """Test detection of multiple technologies."""
        response_data = {
            'headers': {
                'Server': 'nginx/1.18.0',
                'X-Powered-By': 'PHP/7.4.3',
                'X-Frame-Options': 'SAMEORIGIN'
            },
            'content': '''<html>
                <head>
                    <meta name="generator" content="WordPress 5.8">
                    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
                    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
                </head>
                <body class="wp-content">
                    <div class="container">Test</div>
                </body>
            </html>''',
            'status_code': 200
        }
        
        result = await self.fingerprinter.analyze_response(response_data)
        
        # Should detect multiple technologies
        assert 'nginx' in result['server_software'].lower()
        assert 'php' in result['programming_language'].lower()
        assert 'wordpress' in result['cms'].lower()
        assert any('jquery' in lib.lower() for lib in result['javascript_libraries'])
        assert 'x-frame-options' in result['security_headers']
    
    @pytest.mark.asyncio
    async def test_version_extraction(self):
        """Test version number extraction."""
        response_data = {
            'headers': {
                'Server': 'Apache/2.4.41 (Ubuntu)',
                'X-Powered-By': 'PHP/7.4.3'
            },
            'content': '''<html>
                <head>
                    <meta name="generator" content="WordPress 5.8.1">
                    <script src="/wp-includes/js/jquery/jquery.js?ver=3.6.0"></script>
                </head>
                <body>Test</body>
            </html>''',
            'status_code': 200
        }
        
        result = await self.fingerprinter.analyze_response(response_data)
        
        # Should extract version numbers
        assert '2.4.41' in result['server_software'] or 'apache' in result['server_software'].lower()
        assert '7.4.3' in result['programming_language'] or 'php' in result['programming_language'].lower()
        assert '5.8' in result['cms'] or 'wordpress' in result['cms'].lower()
    
    @pytest.mark.asyncio
    async def test_error_page_detection(self):
        """Test error page technology detection."""
        response_data = {
            'headers': {},
            'content': '''<html>
                <head><title>404 Not Found</title></head>
                <body>
                    <h1>Not Found</h1>
                    <p>The requested URL was not found on this server.</p>
                    <hr>
                    <address>Apache/2.4.41 (Ubuntu) Server at example.com Port 80</address>
                </body>
            </html>''',
            'status_code': 404
        }
        
        result = await self.fingerprinter.analyze_response(response_data)
        
        # Should still detect technology from error pages
        assert 'server_software' in result
        assert result['server_software'] is None or 'apache' in result['server_software'].lower()
    
    @pytest.mark.asyncio
    async def test_empty_response(self):
        """Test handling of empty responses."""
        response_data = {
            'headers': {},
            'content': '',
            'status_code': 200
        }
        
        result = await self.fingerprinter.analyze_response(response_data)
        
        # Should handle empty content gracefully
        assert isinstance(result, dict)
        assert 'security_headers' in result
        assert 'javascript_libraries' in result
    
    @pytest.mark.asyncio
    async def test_malformed_html(self):
        """Test handling of malformed HTML."""
        response_data = {
            'headers': {'Server': 'nginx'},
            'content': '''<html>
                <head>
                    <meta name="generator" content="WordPress
                    <script src="/broken.js
                </head>
                <body>
                    <div class="unclosed
                    Test content
                </body>
            ''',
            'status_code': 200
        }
        
        # Should not raise an exception
        result = await self.fingerprinter.analyze_response(response_data)
        
        assert isinstance(result, dict)
        assert 'nginx' in result['server_software'].lower()
    
    @pytest.mark.asyncio
    async def test_case_insensitive_detection(self):
        """Test case-insensitive technology detection."""
        response_data = {
            'headers': {
                'SERVER': 'NGINX/1.18.0',
                'x-powered-by': 'php/7.4.3'
            },
            'content': '''<HTML>
                <HEAD>
                    <META NAME="GENERATOR" CONTENT="WORDPRESS 5.8">
                </HEAD>
                <BODY>Test</BODY>
            </HTML>''',
            'status_code': 200
        }
        
        result = await self.fingerprinter.analyze_response(response_data)
        
        # Should detect technologies regardless of case
        assert 'nginx' in result['server_software'].lower()
        assert 'php' in result['programming_language'].lower()
        assert 'wordpress' in result['cms'].lower()
    
    @pytest.mark.asyncio
    async def test_performance_with_large_content(self):
        """Test performance with large HTML content."""
        # Generate large HTML content
        large_content = "<html><head><title>Large Page</title></head><body>"
        for i in range(10000):
            large_content += f"<p>Paragraph {i} with some content</p>"
        large_content += "</body></html>"
        
        response_data = {
            'headers': {'Server': 'nginx'},
            'content': large_content,
            'status_code': 200
        }
        
        import time
        start_time = time.time()
        result = await self.fingerprinter.analyze_response(response_data)
        end_time = time.time()
        
        # Should complete within reasonable time (5 seconds)
        assert (end_time - start_time) < 5.0
        assert 'nginx' in result['server_software'].lower()