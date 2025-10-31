"""
Technology fingerprinting component for detecting web technologies.
Identifies frameworks, CMS, programming languages, and security headers.
"""

import logging
import re
from typing import Dict, List, Set, Any, Optional
from urllib.parse import urlparse
import aiohttp
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class TechnologyFingerprinter:
    """
    Detects web technologies, frameworks, CMS, and security configurations.
    Uses various fingerprinting techniques including headers, HTML patterns, and JavaScript.
    """
    
    def __init__(self):
        self.technology_signatures = self._load_signatures()
        self.security_headers = self._get_security_headers()
    
    def _load_signatures(self) -> Dict[str, Dict[str, Any]]:
        """
        Load technology detection signatures.
        
        Returns:
            Dictionary of technology signatures
        """
        return {
            # Web Servers
            'apache': {
                'headers': ['server'],
                'patterns': [r'apache', r'httpd'],
                'category': 'web_server'
            },
            'nginx': {
                'headers': ['server'],
                'patterns': [r'nginx'],
                'category': 'web_server'
            },
            'iis': {
                'headers': ['server'],
                'patterns': [r'microsoft-iis', r'iis'],
                'category': 'web_server'
            },
            'cloudflare': {
                'headers': ['server', 'cf-ray'],
                'patterns': [r'cloudflare'],
                'category': 'cdn'
            },
            
            # Programming Languages
            'php': {
                'headers': ['x-powered-by', 'server'],
                'patterns': [r'php', r'\.php'],
                'html_patterns': [r'\.php\?', r'\.php$'],
                'category': 'language'
            },
            'asp.net': {
                'headers': ['x-powered-by', 'x-aspnet-version'],
                'patterns': [r'asp\.net', r'aspnet'],
                'html_patterns': [r'\.aspx', r'__viewstate'],
                'category': 'language'
            },
            'java': {
                'headers': ['server'],
                'patterns': [r'java', r'tomcat', r'jetty'],
                'html_patterns': [r'\.jsp', r'jsessionid'],
                'category': 'language'
            },
            'python': {
                'headers': ['server'],
                'patterns': [r'python', r'django', r'flask', r'wsgi'],
                'category': 'language'
            },
            'nodejs': {
                'headers': ['x-powered-by'],
                'patterns': [r'node\.js', r'express'],
                'category': 'language'
            },
            
            # Frameworks
            'django': {
                'headers': ['server'],
                'patterns': [r'django'],
                'html_patterns': [r'csrfmiddlewaretoken'],
                'category': 'framework'
            },
            'flask': {
                'headers': ['server'],
                'patterns': [r'flask'],
                'category': 'framework'
            },
            'laravel': {
                'html_patterns': [r'laravel_session', r'_token'],
                'category': 'framework'
            },
            'symfony': {
                'html_patterns': [r'symfony'],
                'category': 'framework'
            },
            'rails': {
                'headers': ['x-powered-by'],
                'patterns': [r'ruby', r'rails'],
                'html_patterns': [r'authenticity_token'],
                'category': 'framework'
            },
            'spring': {
                'headers': ['server'],
                'patterns': [r'spring'],
                'html_patterns': [r'jsessionid'],
                'category': 'framework'
            },
            'express': {
                'headers': ['x-powered-by'],
                'patterns': [r'express'],
                'category': 'framework'
            },
            
            # CMS
            'wordpress': {
                'html_patterns': [
                    r'wp-content', r'wp-includes', r'wordpress',
                    r'wp-json', r'/wp-admin/'
                ],
                'category': 'cms'
            },
            'drupal': {
                'html_patterns': [
                    r'drupal', r'/sites/default/', r'drupal\.js',
                    r'sites/all/modules'
                ],
                'category': 'cms'
            },
            'joomla': {
                'html_patterns': [
                    r'joomla', r'/components/', r'/modules/',
                    r'option=com_'
                ],
                'category': 'cms'
            },
            'magento': {
                'html_patterns': [
                    r'magento', r'/skin/frontend/', r'mage/cookies',
                    r'var/connect'
                ],
                'category': 'cms'
            },
            'shopify': {
                'html_patterns': [
                    r'shopify', r'cdn\.shopify\.com', r'myshopify\.com'
                ],
                'category': 'cms'
            },
            
            # JavaScript Libraries
            'jquery': {
                'html_patterns': [r'jquery', r'jquery\.min\.js'],
                'category': 'javascript'
            },
            'react': {
                'html_patterns': [r'react', r'react\.js', r'react\.min\.js'],
                'category': 'javascript'
            },
            'angular': {
                'html_patterns': [r'angular', r'ng-app', r'ng-controller'],
                'category': 'javascript'
            },
            'vue': {
                'html_patterns': [r'vue\.js', r'vue\.min\.js', r'v-if', r'v-for'],
                'category': 'javascript'
            },
            'bootstrap': {
                'html_patterns': [r'bootstrap', r'bootstrap\.css', r'bootstrap\.js'],
                'category': 'css_framework'
            },
            
            # Analytics & Tracking
            'google_analytics': {
                'html_patterns': [r'google-analytics', r'gtag', r'ga\('],
                'category': 'analytics'
            },
            'google_tag_manager': {
                'html_patterns': [r'googletagmanager', r'gtm\.js'],
                'category': 'analytics'
            },
            'facebook_pixel': {
                'html_patterns': [r'facebook\.net/tr', r'fbq\('],
                'category': 'analytics'
            }
        }
    
    def _get_security_headers(self) -> List[str]:
        """
        Get list of important security headers to check.
        
        Returns:
            List of security header names
        """
        return [
            'strict-transport-security',
            'content-security-policy',
            'x-frame-options',
            'x-content-type-options',
            'x-xss-protection',
            'referrer-policy',
            'permissions-policy',
            'feature-policy',
            'expect-ct',
            'public-key-pins'
        ]
    
    async def fingerprint_response(self, response: aiohttp.ClientResponse, html: str = None) -> Dict[str, Any]:
        """
        Fingerprint a web response to detect technologies.
        
        Args:
            response: HTTP response object
            html: HTML content (optional)
            
        Returns:
            Dictionary containing detected technologies
        """
        fingerprint = {
            'url': str(response.url),
            'status_code': response.status,
            'server_software': None,
            'programming_language': [],
            'framework': [],
            'cms': None,
            'javascript_libraries': [],
            'css_frameworks': [],
            'analytics': [],
            'security_headers': {},
            'technologies': [],
            'cdn': []
        }
        
        # Analyze headers
        await self._analyze_headers(response, fingerprint)
        
        # Analyze HTML content if available
        if html:
            await self._analyze_html(html, fingerprint)
        
        # Detect security headers
        self._analyze_security_headers(response, fingerprint)
        
        return fingerprint
    
    async def _analyze_headers(self, response: aiohttp.ClientResponse, fingerprint: Dict[str, Any]):
        """
        Analyze HTTP headers for technology indicators.
        
        Args:
            response: HTTP response object
            fingerprint: Fingerprint dictionary to update
        """
        headers = {k.lower(): v.lower() for k, v in response.headers.items()}
        
        for tech_name, tech_info in self.technology_signatures.items():
            if 'headers' not in tech_info:
                continue
            
            for header_name in tech_info['headers']:
                if header_name in headers:
                    header_value = headers[header_name]
                    
                    # Check patterns
                    patterns = tech_info.get('patterns', [])
                    for pattern in patterns:
                        if re.search(pattern, header_value, re.IGNORECASE):
                            self._add_technology(fingerprint, tech_name, tech_info['category'])
                            break
        
        # Extract server software
        if 'server' in headers:
            fingerprint['server_software'] = headers['server']
    
    async def _analyze_html(self, html: str, fingerprint: Dict[str, Any]):
        """
        Analyze HTML content for technology indicators.
        
        Args:
            html: HTML content
            fingerprint: Fingerprint dictionary to update
        """
        html_lower = html.lower()
        
        for tech_name, tech_info in self.technology_signatures.items():
            if 'html_patterns' not in tech_info:
                continue
            
            patterns = tech_info['html_patterns']
            for pattern in patterns:
                if re.search(pattern, html_lower, re.IGNORECASE):
                    self._add_technology(fingerprint, tech_name, tech_info['category'])
                    break
        
        # Additional HTML analysis
        await self._analyze_html_structure(html, fingerprint)
    
    async def _analyze_html_structure(self, html: str, fingerprint: Dict[str, Any]):
        """
        Analyze HTML structure for additional technology indicators.
        
        Args:
            html: HTML content
            fingerprint: Fingerprint dictionary to update
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Check meta tags
            meta_tags = soup.find_all('meta')
            for meta in meta_tags:
                name = meta.get('name', '').lower()
                content = meta.get('content', '').lower()
                
                if 'generator' in name and content:
                    fingerprint['technologies'].append({
                        'name': content,
                        'category': 'generator',
                        'confidence': 'high'
                    })
            
            # Check script sources
            scripts = soup.find_all('script', src=True)
            for script in scripts:
                src = script.get('src', '').lower()
                self._analyze_script_src(src, fingerprint)
            
            # Check link tags (CSS)
            links = soup.find_all('link', href=True)
            for link in links:
                href = link.get('href', '').lower()
                self._analyze_css_src(href, fingerprint)
            
            # Check for specific HTML patterns
            self._check_html_patterns(soup, fingerprint)
        
        except Exception as e:
            logger.error(f"Error analyzing HTML structure: {e}")
    
    def _analyze_script_src(self, src: str, fingerprint: Dict[str, Any]):
        """
        Analyze script source URLs for technology indicators.
        
        Args:
            src: Script source URL
            fingerprint: Fingerprint dictionary to update
        """
        # Common CDN patterns
        cdn_patterns = {
            'jquery': [r'jquery', r'jquery\.min\.js'],
            'react': [r'react', r'react\.min\.js'],
            'angular': [r'angular', r'angular\.min\.js'],
            'vue': [r'vue\.js', r'vue\.min\.js'],
            'bootstrap': [r'bootstrap\.js', r'bootstrap\.min\.js'],
            'google_analytics': [r'google-analytics\.com', r'gtag'],
            'google_tag_manager': [r'googletagmanager\.com']
        }
        
        for tech_name, patterns in cdn_patterns.items():
            for pattern in patterns:
                if re.search(pattern, src, re.IGNORECASE):
                    category = 'javascript' if tech_name not in ['google_analytics', 'google_tag_manager'] else 'analytics'
                    self._add_technology(fingerprint, tech_name, category)
    
    def _analyze_css_src(self, href: str, fingerprint: Dict[str, Any]):
        """
        Analyze CSS source URLs for technology indicators.
        
        Args:
            href: CSS source URL
            fingerprint: Fingerprint dictionary to update
        """
        css_patterns = {
            'bootstrap': [r'bootstrap', r'bootstrap\.css'],
            'font_awesome': [r'font-awesome', r'fontawesome'],
            'material_ui': [r'material', r'mui']
        }
        
        for tech_name, patterns in css_patterns.items():
            for pattern in patterns:
                if re.search(pattern, href, re.IGNORECASE):
                    self._add_technology(fingerprint, tech_name, 'css_framework')
    
    def _check_html_patterns(self, soup: BeautifulSoup, fingerprint: Dict[str, Any]):
        """
        Check for specific HTML patterns that indicate technologies.
        
        Args:
            soup: BeautifulSoup object
            fingerprint: Fingerprint dictionary to update
        """
        # Check for specific attributes or classes
        patterns = {
            'angular': ['ng-app', 'ng-controller', 'ng-repeat'],
            'vue': ['v-if', 'v-for', 'v-model'],
            'react': ['data-reactroot'],
            'bootstrap': ['container', 'row', 'col-']
        }
        
        html_str = str(soup).lower()
        
        for tech_name, attrs in patterns.items():
            for attr in attrs:
                if attr in html_str:
                    category = 'javascript' if tech_name in ['angular', 'vue', 'react'] else 'css_framework'
                    self._add_technology(fingerprint, tech_name, category)
                    break
    
    def _analyze_security_headers(self, response: aiohttp.ClientResponse, fingerprint: Dict[str, Any]):
        """
        Analyze security headers.
        
        Args:
            response: HTTP response object
            fingerprint: Fingerprint dictionary to update
        """
        headers = {k.lower(): v for k, v in response.headers.items()}
        
        for header_name in self.security_headers:
            if header_name in headers:
                fingerprint['security_headers'][header_name] = headers[header_name]
        
        # Analyze security header quality
        fingerprint['security_score'] = self._calculate_security_score(fingerprint['security_headers'])
    
    def _calculate_security_score(self, security_headers: Dict[str, str]) -> Dict[str, Any]:
        """
        Calculate security score based on present headers.
        
        Args:
            security_headers: Dictionary of security headers
            
        Returns:
            Security score information
        """
        total_headers = len(self.security_headers)
        present_headers = len(security_headers)
        
        score = (present_headers / total_headers) * 100
        
        # Analyze specific headers
        analysis = {
            'score': round(score, 2),
            'total_possible': total_headers,
            'present': present_headers,
            'missing': [h for h in self.security_headers if h not in security_headers],
            'recommendations': []
        }
        
        # Add specific recommendations
        if 'strict-transport-security' not in security_headers:
            analysis['recommendations'].append('Enable HSTS (Strict-Transport-Security)')
        
        if 'content-security-policy' not in security_headers:
            analysis['recommendations'].append('Implement Content Security Policy (CSP)')
        
        if 'x-frame-options' not in security_headers:
            analysis['recommendations'].append('Add X-Frame-Options header to prevent clickjacking')
        
        return analysis
    
    def _add_technology(self, fingerprint: Dict[str, Any], tech_name: str, category: str):
        """
        Add detected technology to fingerprint.
        
        Args:
            fingerprint: Fingerprint dictionary to update
            tech_name: Name of detected technology
            category: Category of technology
        """
        tech_info = {
            'name': tech_name,
            'category': category,
            'confidence': 'medium'
        }
        
        # Add to appropriate category list
        if category == 'language':
            if tech_name not in fingerprint['programming_language']:
                fingerprint['programming_language'].append(tech_name)
        elif category == 'framework':
            if tech_name not in fingerprint['framework']:
                fingerprint['framework'].append(tech_name)
        elif category == 'cms':
            fingerprint['cms'] = tech_name
        elif category == 'javascript':
            if tech_name not in fingerprint['javascript_libraries']:
                fingerprint['javascript_libraries'].append(tech_name)
        elif category == 'css_framework':
            if tech_name not in fingerprint['css_frameworks']:
                fingerprint['css_frameworks'].append(tech_name)
        elif category == 'analytics':
            if tech_name not in fingerprint['analytics']:
                fingerprint['analytics'].append(tech_name)
        elif category == 'cdn':
            if tech_name not in fingerprint['cdn']:
                fingerprint['cdn'].append(tech_name)
        
        # Add to general technologies list
        if tech_info not in fingerprint['technologies']:
            fingerprint['technologies'].append(tech_info)
    
    def get_technology_summary(self, fingerprint: Dict[str, Any]) -> str:
        """
        Generate a human-readable summary of detected technologies.
        
        Args:
            fingerprint: Technology fingerprint
            
        Returns:
            Summary string
        """
        summary_parts = []
        
        if fingerprint.get('server_software'):
            summary_parts.append(f"Server: {fingerprint['server_software']}")
        
        if fingerprint.get('programming_language'):
            langs = ', '.join(fingerprint['programming_language'])
            summary_parts.append(f"Languages: {langs}")
        
        if fingerprint.get('framework'):
            frameworks = ', '.join(fingerprint['framework'])
            summary_parts.append(f"Frameworks: {frameworks}")
        
        if fingerprint.get('cms'):
            summary_parts.append(f"CMS: {fingerprint['cms']}")
        
        if fingerprint.get('javascript_libraries'):
            js_libs = ', '.join(fingerprint['javascript_libraries'])
            summary_parts.append(f"JS Libraries: {js_libs}")
        
        security_score = fingerprint.get('security_score', {}).get('score', 0)
        summary_parts.append(f"Security Score: {security_score}%")
        
        return ' | '.join(summary_parts) if summary_parts else 'No technologies detected'