"""
Advanced URL Analysis Features
Includes: Redirect Following, SSL Check, WHOIS, HTTP Response Analysis, VirusTotal
"""

import requests
import ssl
import socket
import re
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import whois
import time

class AdvancedURLAnalyzer:
    """Advanced URL analysis with multiple verification methods"""
    
    def __init__(self):
        self.timeout = 10
        self.max_redirects = 10
        self.virustotal_api_key = None
    
    def set_virustotal_key(self, api_key):
        """Set VirusTotal API key for integration"""
        self.virustotal_api_key = api_key
    
    # ==================== FEATURE 1: Redirect Following ====================
    def follow_redirects(self, url):
        """
        Follow URL redirects and analyze the chain
        Detects redirect-based phishing attempts
        """
        try:
            redirect_chain = []
            final_url = url
            
            session = requests.Session()
            # Don't follow redirects automatically - we'll track them manually
            response = None
            
            for hop in range(self.max_redirects):
                try:
                    response = session.head(
                        final_url,
                        allow_redirects=False,
                        timeout=self.timeout,
                        verify=True,
                        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                    )
                    
                    redirect_chain.append({
                        'url': final_url,
                        'status_code': response.status_code,
                        'hop': hop + 1
                    })
                    
                    # Check if we have a redirect
                    if response.status_code in [301, 302, 303, 307, 308]:
                        final_url = response.headers.get('Location')
                        if not final_url:
                            break
                        # Handle relative URLs
                        if not final_url.startswith('http'):
                            parsed = urlparse(final_url)
                            if not parsed.scheme:
                                parsed_base = urlparse(redirect_chain[-1]['url'])
                                final_url = f"{parsed_base.scheme}://{parsed_base.netloc}{final_url}"
                    else:
                        break
                
                except Exception as e:
                    break
            
            return {
                'status': 'success',
                'redirect_count': len(redirect_chain) - 1,
                'redirect_chain': redirect_chain,
                'final_url': final_url,
                'is_suspicious': len(redirect_chain) > 3  # More than 3 redirects is suspicious
            }
        
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'redirect_count': 0,
                'redirect_chain': []
            }
    
    # ==================== FEATURE 2: SSL Certificate Check ====================
    def check_ssl_certificate(self, url):
        """
        Validate SSL/TLS certificate
        Detects certificate issues and age
        """
        try:
            parsed_url = urlparse(url)
            hostname = parsed_url.hostname
            
            if not hostname:
                return {'status': 'error', 'error': 'Invalid URL'}
            
            # Connect and get certificate
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            with socket.create_connection((hostname, 443), timeout=self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    der_cert = ssock.getpeercert(binary_form=True)
                    cert = ssl.DER_cert_to_PEM_cert(der_cert)
            
            # Parse certificate
            cert_dict = ssl.DER_cert_to_PEM_cert(der_cert)
            
            # Get certificate info using openssl
            import subprocess
            import tempfile
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pem', mode='w') as f:
                f.write(cert)
                cert_file = f.name
            
            try:
                result = subprocess.run(
                    ['openssl', 'x509', '-in', cert_file, '-text', '-noout'],
                    capture_output=True,
                    text=True
                )
                cert_text = result.stdout
            except:
                # Fallback if openssl not available
                cert_text = ""
            
            # Extract key information
            issued_date = None
            expiry_date = None
            issuer = None
            subject = None
            
            if cert_text:
                # Parse dates
                issued_match = re.search(r'Not Before:\s*(.+)', cert_text)
                expiry_match = re.search(r'Not After:\s*(.+)', cert_text)
                issuer_match = re.search(r'Issuer:\s*(.+)', cert_text)
                subject_match = re.search(r'Subject:\s*(.+)', cert_text)
                
                if issued_match:
                    issued_date = issued_match.group(1).strip()
                if expiry_match:
                    expiry_date = expiry_match.group(1).strip()
                if issuer_match:
                    issuer = issuer_match.group(1).strip()
                if subject_match:
                    subject = subject_match.group(1).strip()
            
            # Get socket certificate details
            sock_cert = None
            try:
                with socket.create_connection((hostname, 443), timeout=self.timeout) as sock:
                    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                        sock_cert = ssock.getpeercert()
            except:
                pass
            
            flags = []
            
            # Check for common issues
            if sock_cert:
                # Check domain match
                cn = dict(x[0] for x in sock_cert.get('subject', []))
                san = sock_cert.get('subjectAltName', [])
                
                domain_match = False
                for alt_type, alt_name in san:
                    if alt_type == 'DNS' and hostname.lower() in alt_name.lower():
                        domain_match = True
                        break
                
                if not domain_match and 'commonName' in cn:
                    if hostname.lower() in cn['commonName'].lower():
                        domain_match = True
                
                if not domain_match:
                    flags.append('domain_mismatch')
            
            # Check certificate age (assume recent if error)
            if 'issued_date' in locals() and issued_date:
                try:
                    # Try to parse (simplified)
                    if '2024' in str(issued_date) or '2025' in str(issued_date):
                        flags.append('recently_issued')
                except:
                    pass
            
            return {
                'status': 'success',
                'hostname': hostname,
                'issuer': issuer or 'Unknown',
                'subject': subject or 'Unknown',
                'issued_date': issued_date or 'Unknown',
                'expiry_date': expiry_date or 'Unknown',
                'flags': flags,
                'is_valid': len(flags) == 0
            }
        
        except socket.gaierror:
            return {'status': 'error', 'error': 'Domain resolution failed'}
        except ssl.SSLError as e:
            return {'status': 'error', 'error': f'SSL Error: {str(e)}'}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    # ==================== FEATURE 3: WHOIS Lookup ====================
    def check_domain_age(self, url):
        """
        Check domain registration age using WHOIS
        Newly registered domains are often used for phishing
        """
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.hostname
            
            if not domain:
                return {'status': 'error', 'error': 'Invalid URL'}
            
            # Remove www if present
            if domain.startswith('www.'):
                domain = domain[4:]
            
            try:
                whois_data = whois.whois(domain)
            except Exception as e:
                return {
                    'status': 'error',
                    'error': f'WHOIS lookup failed: {str(e)}',
                    'domain': domain
                }
            
            flags = []
            
            # Check creation date
            creation_date = whois_data.creation_date
            if isinstance(creation_date, list):
                creation_date = creation_date[0]
            
            if creation_date:
                domain_age_days = (datetime.now() - creation_date).days
                
                # Flag if very new (< 30 days)
                if domain_age_days < 30:
                    flags.append('newly_registered')
                # Flag if very old but also check
                if domain_age_days < 1:
                    flags.append('same_day_registered')
            else:
                domain_age_days = None
            
            # Check expiration date
            expiration_date = whois_data.expiration_date
            if isinstance(expiration_date, list):
                expiration_date = expiration_date[0]
            
            if expiration_date:
                days_to_expiry = (expiration_date - datetime.now()).days
                if days_to_expiry < 30:
                    flags.append('expiring_soon')
            else:
                days_to_expiry = None
            
            return {
                'status': 'success',
                'domain': domain,
                'creation_date': str(creation_date) if creation_date else 'Unknown',
                'expiration_date': str(expiration_date) if expiration_date else 'Unknown',
                'domain_age_days': domain_age_days,
                'days_to_expiry': days_to_expiry,
                'registrar': str(whois_data.registrar) if hasattr(whois_data, 'registrar') else 'Unknown',
                'flags': flags,
                'is_suspicious': len(flags) > 0
            }
        
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    # ==================== FEATURE 4: HTTP Response Analysis ====================
    def analyze_http_response(self, url):
        """
        Fetch and analyze HTTP response for phishing markers
        Detects suspicious content, forms, and scripts
        """
        try:
            response = requests.get(
                url,
                timeout=self.timeout,
                verify=True,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'},
                allow_redirects=True
            )
            
            content = response.text
            soup = BeautifulSoup(content, 'html.parser')
            
            flags = []
            analysis = {
                'status_code': response.status_code,
                'content_length': len(content),
                'title': soup.title.string if soup.title else 'No title',
                'forms_count': len(soup.find_all('form')),
                'login_forms': 0,
                'password_fields': len(soup.find_all('input', {'type': 'password'})),
                'external_forms': 0,
                'suspicious_scripts': 0,
                'has_iframe': len(soup.find_all('iframe')) > 0,
                'flags': flags
            }
            
            # Check for login forms
            forms = soup.find_all('form')
            for form in forms:
                form_action = form.get('action', '').lower()
                form_text = form.get_text().lower()
                
                if 'login' in form_text or 'password' in form_text or 'email' in form_text:
                    analysis['login_forms'] += 1
                    
                    # Check if form submits to external domain
                    if form_action and not form_action.startswith('/'):
                        if url.split('/')[2] not in form_action:
                            flags.append('external_form_submission')
                            analysis['external_forms'] += 1
            
            # Check for password fields
            if analysis['password_fields'] > 0 and 'login' not in url.lower():
                flags.append('unexpected_password_field')
            
            # Check for suspicious scripts
            scripts = soup.find_all('script')
            for script in scripts:
                script_src = script.get('src', '').lower()
                script_content = script.string or ''
                
                # Check for keyloggers, redirects, etc.
                if any(keyword in script_content.lower() for keyword in ['keypress', 'keydown', 'keyup', 'localStorage', 'sessionStorage']):
                    flags.append('suspicious_script_behavior')
                    analysis['suspicious_scripts'] += 1
            
            # Check for iframe (common in phishing)
            if analysis['has_iframe']:
                flags.append('contains_iframe')
            
            # Check meta tags for suspicious redirects
            meta_refresh = soup.find('meta', {'http-equiv': 'refresh'})
            if meta_refresh:
                flags.append('meta_refresh_redirect')
            
            # Check for suspicious keywords in page
            keywords = ['verify', 'confirm', 'validate', 'update account', 'login required']
            page_text = soup.get_text().lower()
            for keyword in keywords:
                if keyword in page_text:
                    # Low confidence flag
                    pass
            
            analysis['is_suspicious'] = len(flags) > 0
            
            return analysis
        
        except requests.exceptions.Timeout:
            return {'status': 'error', 'error': 'Request timeout'}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    # ==================== FEATURE 5: VirusTotal Integration ====================
    def check_virustotal(self, url):
        """
        Check URL reputation on VirusTotal
        Requires API key setup
        """
        if not self.virustotal_api_key:
            return {
                'status': 'error',
                'error': 'VirusTotal API key not configured',
                'note': 'Get free API key from https://www.virustotal.com/api/'
            }
        
        try:
            api_url = 'https://www.virustotal.com/api/v3/urls'
            
            headers = {
                'x-apikey': self.virustotal_api_key
            }
            
            files = {'url': (None, url)}
            
            response = requests.post(
                api_url,
                headers=headers,
                files=files,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                return {
                    'status': 'error',
                    'error': f'VirusTotal API error: {response.status_code}',
                    'message': 'Could not query VirusTotal'
                }
            
            data = response.json()
            
            # Get the URL ID
            url_id = data.get('data', {}).get('id')
            
            if not url_id:
                return {'status': 'error', 'error': 'Invalid VirusTotal response'}
            
            # Get analysis results
            analysis_url = f'https://www.virustotal.com/api/v3/urls/{url_id}'
            analysis_response = requests.get(
                analysis_url,
                headers=headers,
                timeout=self.timeout
            )
            
            if analysis_response.status_code != 200:
                return {'status': 'error', 'error': 'Could not fetch analysis'}
            
            analysis_data = analysis_response.json()
            attributes = analysis_data.get('data', {}).get('attributes', {})
            last_analysis_stats = attributes.get('last_analysis_stats', {})
            
            return {
                'status': 'success',
                'url': url,
                'malicious': last_analysis_stats.get('malicious', 0),
                'suspicious': last_analysis_stats.get('suspicious', 0),
                'undetected': last_analysis_stats.get('undetected', 0),
                'harmless': last_analysis_stats.get('harmless', 0),
                'timeout': last_analysis_stats.get('timeout', 0),
                'total_vendors': sum(last_analysis_stats.values()),
                'is_flagged': last_analysis_stats.get('malicious', 0) > 0 or last_analysis_stats.get('suspicious', 0) > 0
            }
        
        except Exception as e:
            return {'status': 'error', 'error': f'VirusTotal check failed: {str(e)}'}
    
    def get_all_checks(self, url, include_virustotal=False):
        """
        Run all available checks and return combined results
        """
        results = {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'redirects': self.follow_redirects(url),
            'ssl_certificate': self.check_ssl_certificate(url) if url.startswith('https') else {'status': 'skipped', 'reason': 'Not HTTPS'},
            'domain_age': self.check_domain_age(url),
            'http_analysis': self.analyze_http_response(url),
        }
        
        if include_virustotal:
            results['virustotal'] = self.check_virustotal(url)
        
        return results
