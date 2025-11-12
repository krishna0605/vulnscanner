"""
HTML parsing and data extraction component.
Extracts links, forms, scripts, and other relevant data from HTML content.
"""

import logging
import re
from typing import Dict, List
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup, Comment

logger = logging.getLogger(__name__)


class HTMLParser:
    """
    HTML parser for extracting links, forms, and other security-relevant data.
    Uses BeautifulSoup for robust HTML parsing and data extraction.
    """
    
    def __init__(self):
        self.csrf_patterns = [
            r'csrf[_-]?token',
            r'_token',
            r'authenticity[_-]?token',
            r'__RequestVerificationToken',
            r'csrfmiddlewaretoken'
        ]
        
        # Compile regex patterns for performance
        self.csrf_regex = [re.compile(pattern, re.IGNORECASE) for pattern in self.csrf_patterns]
    
    async def parse_html(self, html_content: str, base_url: str) -> Dict:
        """
        Parse HTML content and extract all relevant data.
        
        Args:
            html_content: Raw HTML content
            base_url: Base URL for resolving relative links
            
        Returns:
            Dict containing extracted data (links, forms, scripts, etc.)
        """
        try:
            # Try fast built-in parser first; fallback to lxml/html5lib if available
            soup = BeautifulSoup(html_content or "", 'html.parser')
            if not soup or not soup.contents:
                try:
                    soup = BeautifulSoup(html_content or "", 'lxml')  # type: ignore
                except Exception:
                    try:
                        soup = BeautifulSoup(html_content or "", 'html5lib')  # type: ignore
                    except Exception:
                        pass
            
            return {
                'links': self._extract_links(soup, base_url),
                'forms': self._extract_forms(soup, base_url),
                'scripts': self._extract_scripts(soup, base_url),
                'meta': self._extract_meta_tags(soup),
                'comments': self._extract_comments(soup),
                'inputs': self._extract_inputs(soup),
                'images': self._extract_images(soup, base_url),
                'stylesheets': self._extract_stylesheets(soup, base_url),
                'title': self._extract_title(soup),
                'headings': self._extract_headings(soup),
                'external_resources': self._extract_external_resources(soup, base_url)
            }
        
        except Exception as e:
            logger.error(f"Error parsing HTML: {e}")
            return {}
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Extract all links from the HTML."""
        links = []
        seen_urls = set()
        
        try:
            # Extract from <a> tags
            for link in soup.find_all('a', href=True):
                href = link['href'].strip()
                if href and not href.startswith('#') and not href.startswith('javascript:'):
                    absolute_url = urljoin(base_url, href)
                    if absolute_url not in seen_urls:
                        links.append({'url': absolute_url, 'text': link.get_text(strip=True)})
                        seen_urls.add(absolute_url)
            
            # Extract from <area> tags (image maps)
            for area in soup.find_all('area', href=True):
                href = area['href'].strip()
                if href and not href.startswith('#') and not href.startswith('javascript:'):
                    absolute_url = urljoin(base_url, href)
                    if absolute_url not in seen_urls:
                        links.append({'url': absolute_url, 'text': area.get('alt', '')})
                        seen_urls.add(absolute_url)
            
            # Extract from <link> tags (alternate pages, etc.)
            for link in soup.find_all('link', href=True):
                rel = link.get('rel', [])
                if isinstance(rel, str):
                    rel = [rel]
                
                # Only include certain link types
                if any(r in ['alternate', 'next', 'prev', 'canonical'] for r in rel):
                    href = link['href'].strip()
                    if href:
                        absolute_url = urljoin(base_url, href)
                        if absolute_url not in seen_urls:
                            links.append({'url': absolute_url, 'text': ''})
                            seen_urls.add(absolute_url)
        
        except Exception as e:
            logger.error(f"Error extracting links: {e}")
        
        return links
    
    def _extract_forms(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Extract all forms and their details."""
        forms = []
        
        try:
            for form in soup.find_all('form'):
                form_data = {
                    'action': self._get_form_action(form, base_url),
                    'method': form.get('method', 'GET').lower(),
                    'enctype': form.get('enctype', 'application/x-www-form-urlencoded'),
                    'fields': self._extract_form_fields(form),
                    'csrf_tokens': self._extract_csrf_tokens(form),
                    'auth_required': self._detect_auth_form(form),
                    'file_upload': self._has_file_upload(form),
                    'hidden_fields': self._extract_hidden_fields(form)
                }
                
                forms.append(form_data)
        
        except Exception as e:
            logger.error(f"Error extracting forms: {e}")
        
        return forms
    
    def _get_form_action(self, form, base_url: str) -> str:
        """Get the absolute action URL for a form."""
        action = form.get('action', '')
        if not action:
            return base_url
        return urljoin(base_url, action)
    
    def _extract_form_fields(self, form) -> List[Dict]:
        """Extract all form fields and their properties."""
        fields = []
        
        try:
            # Extract input fields
            for input_tag in form.find_all(['input', 'textarea', 'select']):
                field_data = {
                    'tag': input_tag.name,
                    'type': input_tag.get('type', 'text'),
                    'name': input_tag.get('name', ''),
                    'id': input_tag.get('id', ''),
                    'value': input_tag.get('value', ''),
                    'placeholder': input_tag.get('placeholder', ''),
                    'required': input_tag.has_attr('required'),
                    'disabled': input_tag.has_attr('disabled'),
                    'readonly': input_tag.has_attr('readonly'),
                    'maxlength': input_tag.get('maxlength', ''),
                    'pattern': input_tag.get('pattern', ''),
                    'autocomplete': input_tag.get('autocomplete', '')
                }
                
                # Extract options for select fields
                if input_tag.name == 'select':
                    options = []
                    for option in input_tag.find_all('option'):
                        options.append({
                            'value': option.get('value', ''),
                            'text': option.get_text(strip=True),
                            'selected': option.has_attr('selected')
                        })
                    field_data['options'] = options
                
                fields.append(field_data)
        
        except Exception as e:
            logger.error(f"Error extracting form fields: {e}")
        
        return fields
    
    def _extract_csrf_tokens(self, form) -> List[Dict]:
        """Extract CSRF tokens from the form."""
        tokens = []
        
        try:
            # Look for hidden inputs with CSRF-like names
            for input_tag in form.find_all('input', type='hidden'):
                name = input_tag.get('name', '').lower()
                value = input_tag.get('value', '')
                
                for regex in self.csrf_regex:
                    if regex.search(name) and value:
                        tokens.append({
                            'name': input_tag.get('name', ''),
                            'value': value,
                            'type': 'hidden_input'
                        })
                        break
            
            # Look for meta tags with CSRF tokens
            meta_tags = form.find_all('meta')
            for meta in meta_tags:
                name = meta.get('name', '').lower()
                content = meta.get('content', '')
                
                for regex in self.csrf_regex:
                    if regex.search(name) and content:
                        tokens.append({
                            'name': meta.get('name', ''),
                            'value': content,
                            'type': 'meta_tag'
                        })
                        break
        
        except Exception as e:
            logger.error(f"Error extracting CSRF tokens: {e}")
        
        return tokens
    
    def _detect_auth_form(self, form) -> bool:
        """Detect if this is an authentication form."""
        try:
            # Look for password fields
            if form.find('input', type='password'):
                return True
            
            # Look for common auth field names
            auth_indicators = ['username', 'email', 'login', 'user', 'password', 'pass']
            for input_tag in form.find_all('input'):
                name = input_tag.get('name', '').lower()
                id_attr = input_tag.get('id', '').lower()
                
                if any(indicator in name or indicator in id_attr for indicator in auth_indicators):
                    return True
            
            # Check form action for auth-related paths
            action = form.get('action', '').lower()
            auth_paths = ['login', 'signin', 'auth', 'authenticate']
            if any(path in action for path in auth_paths):
                return True
        
        except Exception as e:
            logger.error(f"Error detecting auth form: {e}")
        
        return False
    
    def _has_file_upload(self, form) -> bool:
        """Check if form has file upload capability."""
        try:
            # Check for file input type
            if form.find('input', type='file'):
                return True
            
            # Check for multipart encoding
            enctype = form.get('enctype', '').lower()
            if 'multipart/form-data' in enctype:
                return True
        
        except Exception as e:
            logger.error(f"Error checking file upload: {e}")
        
        return False
    
    def _extract_hidden_fields(self, form) -> List[Dict]:
        """Extract hidden form fields."""
        hidden_fields = []
        
        try:
            for input_tag in form.find_all('input', type='hidden'):
                hidden_fields.append({
                    'name': input_tag.get('name', ''),
                    'value': input_tag.get('value', ''),
                    'id': input_tag.get('id', '')
                })
        
        except Exception as e:
            logger.error(f"Error extracting hidden fields: {e}")
        
        return hidden_fields
    
    def _extract_scripts(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Extract script tags and their sources."""
        scripts = []
        
        try:
            for script in soup.find_all('script'):
                script_data = {
                    'type': script.get('type', 'text/javascript'),
                    'async': script.has_attr('async'),
                    'defer': script.has_attr('defer'),
                    'inline': not script.get('src'),
                    'content_length': len(script.get_text()) if not script.get('src') else 0
                }
                
                # Add src for external scripts only
                if script.get('src'):
                    script_data['src'] = urljoin(base_url, script.get('src'))
                
                # Extract inline script content (first 500 chars for analysis)
                if not script.get('src'):
                    content = script.get_text(strip=True)
                    script_data['content'] = content[:500] if content else ''
                
                scripts.append(script_data)
        
        except Exception as e:
            logger.error(f"Error extracting scripts: {e}")
        
        return scripts
    
    def _extract_meta_tags(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract meta tags."""
        meta_tags = []
        
        try:
            for meta in soup.find_all('meta'):
                meta_data = {
                    'name': meta.get('name', ''),
                    'property': meta.get('property', ''),
                    'content': meta.get('content', ''),
                    'http_equiv': meta.get('http-equiv', ''),
                    'charset': meta.get('charset', '')
                }
                
                # Only include meta tags with meaningful content
                if any(meta_data.values()):
                    meta_tags.append(meta_data)
        
        except Exception as e:
            logger.error(f"Error extracting meta tags: {e}")
        
        return meta_tags
    
    def _extract_comments(self, soup: BeautifulSoup) -> List[str]:
        """Extract HTML comments."""
        comments = []
        
        try:
            for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
                comment_text = comment.strip()
                if comment_text and len(comment_text) > 5:  # Skip very short comments
                    comments.append(comment_text[:500])  # Limit comment length
        
        except Exception as e:
            logger.error(f"Error extracting comments: {e}")
        
        return comments
    
    def _extract_inputs(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract all input elements (not in forms)."""
        inputs = []
        
        try:
            # Find inputs not inside forms
            for input_tag in soup.find_all('input'):
                if not input_tag.find_parent('form'):
                    inputs.append({
                        'type': input_tag.get('type', 'text'),
                        'name': input_tag.get('name', ''),
                        'id': input_tag.get('id', ''),
                        'value': input_tag.get('value', ''),
                        'placeholder': input_tag.get('placeholder', '')
                    })
        
        except Exception as e:
            logger.error(f"Error extracting inputs: {e}")
        
        return inputs
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Extract image sources."""
        images = []
        
        try:
            for img in soup.find_all('img', src=True):
                images.append({
                    'src': urljoin(base_url, img['src']),
                    'alt': img.get('alt', ''),
                    'title': img.get('title', ''),
                    'width': img.get('width', ''),
                    'height': img.get('height', '')
                })
        
        except Exception as e:
            logger.error(f"Error extracting images: {e}")
        
        return images
    
    def _extract_stylesheets(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract stylesheet links."""
        stylesheets = []
        
        try:
            for link in soup.find_all('link', rel='stylesheet', href=True):
                stylesheets.append(urljoin(base_url, link['href']))
        
        except Exception as e:
            logger.error(f"Error extracting stylesheets: {e}")
        
        return stylesheets
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title."""
        try:
            title_tag = soup.find('title')
            if title_tag:
                return title_tag.get_text(strip=True)
        except Exception as e:
            logger.error(f"Error extracting title: {e}")
        
        return ""
    
    def _extract_headings(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        """Extract heading tags (h1-h6)."""
        headings = {}
        
        try:
            for i in range(1, 7):
                tag_name = f'h{i}'
                heading_texts = []
                
                for heading in soup.find_all(tag_name):
                    text = heading.get_text(strip=True)
                    if text:
                        heading_texts.append(text[:200])  # Limit heading length
                
                if heading_texts:
                    headings[tag_name] = heading_texts
        
        except Exception as e:
            logger.error(f"Error extracting headings: {e}")
        
        return headings
    
    def _extract_external_resources(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Extract external resources (CDNs, third-party scripts, etc.)."""
        external_resources = []
        base_domain = urlparse(base_url).netloc
        
        try:
            # Check scripts
            for script in soup.find_all('script', src=True):
                src = script['src']
                absolute_url = urljoin(base_url, src)
                resource_domain = urlparse(absolute_url).netloc
                
                if resource_domain != base_domain:
                    external_resources.append({
                        'type': 'script',
                        'url': absolute_url,
                        'domain': resource_domain
                    })
            
            # Check stylesheets
            for link in soup.find_all('link', rel='stylesheet', href=True):
                href = link['href']
                absolute_url = urljoin(base_url, href)
                resource_domain = urlparse(absolute_url).netloc
                
                if resource_domain != base_domain:
                    external_resources.append({
                        'type': 'stylesheet',
                        'url': absolute_url,
                        'domain': resource_domain
                    })
            
            # Check images
            for img in soup.find_all('img', src=True):
                src = img['src']
                absolute_url = urljoin(base_url, src)
                resource_domain = urlparse(absolute_url).netloc
                
                if resource_domain != base_domain:
                    external_resources.append({
                        'type': 'image',
                        'url': absolute_url,
                        'domain': resource_domain
                    })
        
        except Exception as e:
            logger.error(f"Error extracting external resources: {e}")
        
        return external_resources