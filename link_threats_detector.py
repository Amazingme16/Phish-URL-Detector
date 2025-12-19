"""
Link Threats Detector Module
Comprehensive URL threat detection using PhishFort-inspired detection patterns
Detects: Malicious links, phishing tactics, domain spoofing, suspicious redirects, credential harvesting
"""

import re
from urllib.parse import urlparse, parse_qs
import requests
from datetime import datetime
import json


class LinkThreatsDetector:
    """Advanced link threats detection using multiple threat vectors"""
    
    def __init__(self):
        self.timeout = 8
        self.threat_indicators = {
            'credential_harvesting': [],
            'domain_spoofing': [],
            'redirect_chains': [],
            'suspicious_parameters': [],
            'malicious_patterns': [],
            'brand_impersonation': []
        }
        
        # Crypto wallet keywords
        self.crypto_keywords = [
            'wallet', 'metamask', 'ledger', 'trezor', 'trustwallet', 'phrase', 
            'recovery', 'seed', 'private_key', 'connect', 'airdrop', 'claim'
        ]
        
        # Zero-width characters (invisible)
        self.zero_width_chars = [
            '\u200b', '\u200c', '\u200d', '\ufeff', '\u2060'
        ]

        # Common credential harvesting keywords
        self.credential_keywords = [
            'login', 'signin', 'account', 'verify', 'confirm', 'authenticate',
            'password', 'credential', 'update', 'validate', 'secure', 'authorize',
            'reactivate', 'confirm-identity', 'confirm_identity'
        ]
        
        # Suspicious parameter patterns
        self.suspicious_params = [
            'redirect', 'return_url', 'returnurl', 'back', 'callback',
            'next', 'forward', 'url', 'goto', 'destination', 'target'
        ]
        
        # Common brand names for impersonation detection
        self.protected_brands = [
            'paypal', 'amazon', 'apple', 'microsoft', 'google', 'facebook', 'twitter',
            'instagram', 'linkedin', 'ebay', 'banking', 'bank', 'irs', 'fedex', 'ups',
            'dhl', 'netflix', 'spotify', 'dropbox', 'icloud', 'gmail', 'outlook',
            'crypto', 'coinbase', 'binance', 'metamask', 'wallet', 'exchange',
            'ethereum', 'bitcoin', 'blockchain', 'opensea', 'chase', 'wellsfargo',
            'bofa', 'hsbc', 'barclays', 'citibank', 'tiktok', 'snapchat', 'reddit',
            'kraken', 'kucoin', 'ledger', 'trustwallet', 'wells-fargo'
        ]
        
        # Known phishing tactics
        self.phishing_tactics = {
            'urgency': ['urgent', 'immediately', 'action required', 'expired', 'suspended', 'locked'],
            'fear': ['danger', 'alert', 'warning', 'security', 'compromised', 'malware'],
            'authority': ['official', 'admin', 'support', 'security team', 'verification'],
            'deception': ['confirm', 'validate', 'update account', 're-activate']
        }
        
    def detect_all_threats(self, url):
        """
        Comprehensive threat detection across all vectors
        Returns dict with all threat indicators found
        """
        threats = {
            'threat_level': 'low',
            'threat_score': 0,
            'threats_found': [],
            'details': {
                'credential_harvesting': self._detect_credential_harvesting(url),
                'domain_spoofing': self._detect_domain_spoofing(url),
                'redirect_analysis': self._analyze_redirect_risk(url),
                'suspicious_parameters': self._find_suspicious_parameters(url),
                'malicious_patterns': self._detect_malicious_patterns(url),
                'brand_impersonation': self._detect_brand_impersonation(url),
                'typosquatting': self._detect_typosquatting(url),
                'suspicious_tld': self._check_suspicious_tld(url),
                'obfuscation': self._detect_obfuscation(url),
                'zero_width_chars': self._detect_zero_width_chars(url),
                'crypto_targeting': self._detect_crypto_targeting(url)
            }
        }
        
        # Calculate threat score
        threats['threat_score'] = self._calculate_threat_score(threats['details'])
        threats['threat_level'] = self._get_threat_level(threats['threat_score'])
        
        # Collect all threats found
        for category, details in threats['details'].items():
            if details.get('detected'):
                threats['threats_found'].append(category)
        
        return threats
    
    def _detect_credential_harvesting(self, url):
        """
        Detect credential harvesting indicators
        Looks for login forms, password fields, authentication pages
        """
        result = {
            'detected': False,
            'indicators': [],
            'risk': 'none'
        }
        
        parsed = urlparse(url)
        path_and_query = parsed.path + parsed.query
        path_lower = path_and_query.lower()
        
        # Check for credential harvesting keywords
        for keyword in self.credential_keywords:
            if keyword in path_lower:
                result['indicators'].append(f"Contains '{keyword}' in URL path")
                result['detected'] = True
                result['risk'] = 'high'
        
        # Check for suspicious query parameters
        if parsed.query:
            if 'login' in path_lower or 'signin' in path_lower:
                result['indicators'].append("Potential login redirect parameter")
                result['detected'] = True
                result['risk'] = 'high'
        
        # Check for fake form patterns
        if re.search(r'(form|login|signin|password|account)', path_lower):
            result['indicators'].append("URL structure suggests form-based phishing")
            result['detected'] = True
            result['risk'] = 'high'
        
        return result
    
    def _detect_domain_spoofing(self, url):
        """
        Detect domain spoofing attempts
        Looks for homograph attacks, lookalike domains, Unicode abuse
        """
        result = {
            'detected': False,
            'indicators': [],
            'risk': 'none'
        }
        
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Remove www if present
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # Check for homograph attacks (similar-looking characters)
        homograph_patterns = [
            (r'0(?=l|L|I|1)', 'Zero/Letter confusion'),
            (r'l(?=0|O)', 'Letter/Number confusion'),
            (r'rn(?=m)', 'RN/M confusion'),
            (r'googIe', 'Capital I in brand name'),
            (r'paypaI', 'Capital I in brand name'),
            (r'microsoft\.', 'Microsoft spoofing extension'),
            (r'apple-.*id', 'Fake Apple ID pattern')
        ]
        
        for pattern, desc in homograph_patterns:
            if re.search(pattern, domain):
                result['indicators'].append(f"Possible homograph/spoofing: {desc}")
                result['detected'] = True
                result['risk'] = 'high'
        
        # Check for Punycode
        if domain.startswith('xn--'):
            result['indicators'].append("Punycode detected (often used for internationalized homographs)")
            result['detected'] = True
            result['risk'] = 'high'
        
        # Check for extra subdomains (subdomain stuffing)
        subdomain_count = domain.count('.')
        if subdomain_count > 3:
            result['indicators'].append("Excessive subdomains (subdomain stuffing)")
            result['detected'] = True
            result['risk'] = 'medium'
        
        # Check for Unicode characters in domain
        try:
            domain.encode('ascii')
        except UnicodeEncodeError:
            result['indicators'].append("Unicode/internationalized domain (possible homograph)")
            result['detected'] = True
            result['risk'] = 'high'
        
        return result
    
    def _analyze_redirect_risk(self, url):
        """
        Analyze redirect chain risk
        Detects suspicious redirect patterns and chains
        """
        result = {
            'detected': False,
            'redirect_count': 0,
            'indicators': [],
            'risk': 'none'
        }
        
        parsed = urlparse(url)
        
        # Check for redirect parameters
        redirect_params = parse_qs(parsed.query)
        for param_key in redirect_params.keys():
            if param_key.lower() in self.suspicious_params:
                redirect_url = redirect_params[param_key][0] if redirect_params[param_key] else ''
                result['indicators'].append(f"Redirect parameter '{param_key}' detected")
                result['detected'] = True
                result['risk'] = 'high'
                
                # Check if redirect goes to different domain
                if redirect_url:
                    try:
                        redirect_parsed = urlparse(redirect_url)
                        if redirect_parsed.netloc and redirect_parsed.netloc != parsed.netloc:
                            result['indicators'].append(f"Cross-domain redirect detected")
                            result['risk'] = 'critical'
                    except:
                        pass
        
        # Check for data: URI redirects (can bypass filtering)
        if 'data:' in url or 'javascript:' in url:
            result['indicators'].append("Data/JavaScript URI detected (potential bypass)")
            result['detected'] = True
            result['risk'] = 'critical'
        
        return result
    
    def _find_suspicious_parameters(self, url):
        """
        Find suspicious query parameters
        Detects obfuscation, encoding, suspicious values
        """
        result = {
            'detected': False,
            'parameters': [],
            'indicators': [],
            'risk': 'none'
        }
        
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        
        if not params:
            result['parameters'] = []
            return result
        
        for key, values in params.items():
            param_info = {'name': key, 'value': values[0] if values else ''}
            
            # Check for base64 encoded values
            if len(values[0]) > 20 and re.match(r'^[A-Za-z0-9+/=]+$', values[0]):
                result['indicators'].append(f"Base64-encoded parameter '{key}'")
                result['detected'] = True
                result['risk'] = 'medium'
            
            # Check for URL-encoded suspicious content
            if '%2' in values[0] or '%3' in values[0]:
                result['indicators'].append(f"URL-encoded suspicious value in '{key}'")
                result['detected'] = True
                result['risk'] = 'medium'
            
            # Check for script injection patterns
            if re.search(r'(script|javascript|onerror|onclick)', values[0], re.I):
                result['indicators'].append(f"Potential XSS payload in '{key}'")
                result['detected'] = True
                result['risk'] = 'high'
            
            result['parameters'].append(param_info)
        
        return result
    
    def _detect_malicious_patterns(self, url):
        """
        Detect known malicious URL patterns
        Looks for exploit kits, malware distribution, known bad patterns
        """
        result = {
            'detected': False,
            'patterns': [],
            'risk': 'none'
        }
        
        url_lower = url.lower()
        
        # Exploit kit patterns
        exploit_patterns = [
            (r'(admin|wp-admin|phpmyadmin)', 'Potential admin panel targeting'),
            (r'(shell|webshell|aspx|cfm)', 'Web shell delivery pattern'),
            (r'(/upload|/files|/download)', 'Suspicious upload/download path'),
            (r'(eval|base64_decode|gzip)', 'Obfuscation techniques'),
            (r'(cmd|exec|system|passthru)', 'Command execution patterns'),
        ]
        
        for pattern, desc in exploit_patterns:
            if re.search(pattern, url_lower):
                result['patterns'].append(f"{desc}: {pattern}")
                result['detected'] = True
                result['risk'] = 'high'
        
        # Check for suspicious file extensions
        suspicious_extensions = ['.exe', '.scr', '.bat', '.cmd', '.pif', '.zip']
        if any(ext in url_lower for ext in suspicious_extensions):
            result['patterns'].append("Suspicious executable file extension")
            result['detected'] = True
            result['risk'] = 'critical'
        
        return result
    
    def _detect_brand_impersonation(self, url):
        """
        Detect brand impersonation attempts
        Identifies lookalike domains mimicking legitimate brands
        """
        result = {
            'detected': False,
            'impersonated_brands': [],
            'risk': 'none'
        }
        
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Remove www
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # Check each protected brand
        for brand in self.protected_brands:
            if brand in domain:
                # Verify it's not the legitimate domain
                if domain != f"{brand}.com" and \
                   domain != f"{brand}.org" and \
                   domain != f"{brand}.net" and \
                   domain != f"www.{brand}.com":
                    
                    result['impersonated_brands'].append({
                        'brand': brand,
                        'domain': domain,
                        'suspicious_variations': self._find_brand_variations(domain, brand)
                    })
                    result['detected'] = True
                    result['risk'] = 'high'
        
        return result
    
    def _find_brand_variations(self, domain, brand):
        """Find variations/mutations of legitimate brand names"""
        variations = []
        
        # Check for insertions/modifications
        if brand in domain and domain != brand:
            variations.append("Brand name embedded in different domain")
        
        # Check for common misspellings/variations
        common_variations = {
            'paypal': ['paypai', 'paypa1', 'pay-pal'],
            'amazon': ['amaz0n', 'amazo-n', 'amzn-'],
            'apple': ['appl3', 'app1e', 'aple'],
            'google': ['g00gle', 'gogle', 'goog1e'],
        }
        
        if brand in common_variations:
            for variation in common_variations[brand]:
                if variation in domain:
                    variations.append(f"Common misspelling: {variation}")
        
        return variations
    
    def _detect_typosquatting(self, url):
        """
        Detect typosquatting attacks
        Identifies domains similar to legitimate ones
        """
        result = {
            'detected': False,
            'indicators': [],
            'risk': 'none'
        }
        
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Check for character substitution patterns
        substitution_patterns = {
            '0': 'O',
            '1': 'L|I',
            '3': 'E',
            '4': 'A',
            '5': 'S',
            '7': 'T',
            '8': 'B',
        }
        
        # Look for number/letter substitutions
        if re.search(r'\d', domain):
            for num, letters in substitution_patterns.items():
                if num in domain:
                    result['indicators'].append(f"Digit '{num}' substituting letter(s) {letters}")
                    result['detected'] = True
                    result['risk'] = 'high'
        
        # Check for removed vowels
        if re.search(r'[bcdfghjklmnprstvwxyz]{3,}', domain):
            result['indicators'].append("Suspicious vowel pattern (possible typosquatting)")
            result['detected'] = True
            result['risk'] = 'medium'
        
        return result
    
    def _check_suspicious_tld(self, url):
        """
        Check for suspicious top-level domains
        Identifies uncommon or high-risk TLDs
        """
        result = {
            'detected': False,
            'tld': '',
            'risk': 'none',
            'indicators': []
        }
        
        parsed = urlparse(url)
        domain = parsed.netloc
        
        # Extract TLD
        parts = domain.split('.')
        if len(parts) >= 2:
            tld = parts[-1].lower()
            result['tld'] = tld
            
            # Check against free/suspicious TLDs
            suspicious_tlds = [
                'tk', 'ml', 'ga', 'cf',  # Freenom free TLDs
                'top', 'win', 'download', 'men', 'buzz', 'cloud',  # Cheap TLDs
                'accountant', 'space', 'website'  # High-abuse TLDs
            ]
            
            if tld in suspicious_tlds:
                result['indicators'].append(f"Suspicious TLD '.{tld}' commonly used in phishing")
                result['detected'] = True
                result['risk'] = 'high'
            
            # Check for new gTLDs with mixed case
            if not tld.islower() and tld != tld.upper():
                result['indicators'].append("Mixed-case TLD (possible obfuscation)")
                result['detected'] = True
                result['risk'] = 'medium'
        
        return result
    
    def _detect_obfuscation(self, url):
        """
        Detect URL obfuscation techniques
        Identifies encoding and hiding tactics
        """
        result = {
            'detected': False,
            'techniques': [],
            'risk': 'none'
        }
        
        # Check for IP address instead of domain
        if re.search(r'http[s]?://\d+\.\d+\.\d+\.\d+', url):
            result['techniques'].append("Direct IP address used (domain spoofing)")
            result['detected'] = True
            result['risk'] = 'high'
        
        # Check for hexadecimal IP encoding
        if re.search(r'0x[0-9a-fA-F]+', url):
            result['techniques'].append("Hexadecimal encoding detected")
            result['detected'] = True
            result['risk'] = 'high'
        
        # Check for excessive URL encoding
        if url.count('%') > 5:
            result['techniques'].append("Excessive URL encoding (likely obfuscation)")
            result['detected'] = True
            result['risk'] = 'high'
        
        # Check for @symbol (can hide real domain)
        if '@' in url:
            result['techniques'].append("@ symbol in URL (domain masking)")
            result['detected'] = True
            result['risk'] = 'critical'
        
        # Check for very long URLs
        if len(url) > 200:
            result['techniques'].append("Abnormally long URL (possible obfuscation)")
            result['detected'] = True
            result['risk'] = 'medium'
        
        return result

    def _detect_zero_width_chars(self, url):
        """
        Detect zero-width characters often used to bypass filters
        """
        result = {
            'detected': False,
            'chars_found': [],
            'risk': 'none'
        }
        
        for char in self.zero_width_chars:
            if char in url:
                result['chars_found'].append(f"U+{ord(char):04X}")
                result['detected'] = True
                result['risk'] = 'critical'
                
        return result

    def _detect_crypto_targeting(self, url):
        """
        Detect cryptocurrency-specific phishing targeting
        """
        result = {
            'detected': False,
            'indicators': [],
            'risk': 'none'
        }
        
        url_lower = url.lower()
        
        # Check for crypto keywords in domain/path
        for keyword in self.crypto_keywords:
            if keyword in url_lower:
                # Higher risk if combined with 'login' or 'confirm'
                if any(k in url_lower for k in ['login', 'confirm', 'validate']):
                    result['indicators'].append(f"Crypto keyword '{keyword}' with suspicious action")
                    result['risk'] = 'critical'
                    result['detected'] = True
                elif keyword in urlparse(url).netloc:
                    result['indicators'].append(f"Crypto keyword '{keyword}' in domain")
                    result['risk'] = 'high'
                    result['detected'] = True
                    
        return result
    
    def _calculate_threat_score(self, details):
        """
        Calculate overall threat score from all indicators
        Scale: 0-100
        """
        score = 0
        risk_weights = {
            'critical': 25,
            'high': 15,
            'medium': 8,
            'low': 3
        }
        
        for category, info in details.items():
            if isinstance(info, dict) and info.get('detected'):
                risk = info.get('risk', 'medium')
                weight = risk_weights.get(risk, 5)
                score += weight
        
        return min(score, 100)
    
    def _get_threat_level(self, score):
        """
        Map threat score to threat level
        """
        if score >= 75:
            return 'critical'
        elif score >= 50:
            return 'high'
        elif score >= 25:
            return 'medium'
        elif score >= 10:
            return 'low'
        else:
            return 'minimal'


# Initialize detector for easy use
link_threats_detector = LinkThreatsDetector()
