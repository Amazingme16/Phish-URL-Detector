"""
URL Feature Extraction Module
Extracts 16+ key features from URLs for phishing detection
"""

import re
import urllib.parse
import ipaddress
import math
from datetime import datetime
from collections import Counter
import unicodedata

class URLFeatureExtractor:
    """Extracts features from URLs for ML-based phishing detection"""
    
    def __init__(self):
        self.suspicious_keywords = [
            # Original keywords
            'secure', 'login', 'verify', 'account', 'update', 'confirm',
            'banking', 'paypal', 'amazon', 'apple', 'microsoft', 'free',
            # PhishSage expanded keywords
            'admin', 'access', 'alert', 'auth', 'authenticate', 'bank',
            'bill', 'billing', 'cert', 'check', 'claim', 'click',
            'confirm', 'connect', 'contact', 'email', 'expire', 'expired',
            'fraud', 'free', 'giftcard', 'grant', 'help', 'id',
            'identity', 'important', 'info', 'install', 'instant',
            'invoice', 'limited', 'link', 'locked', 'login', 'mail',
            'member', 'message', 'mobile', 'notify', 'offer', 'online',
            'password', 'pay', 'payment', 'phone', 'pin', 'reactivate',
            'register', 'renew', 'reply', 'reset', 'restore', 'review',
            'safe', 'secure', 'security', 'session', 'sign', 'signin',
            'signup', 'special', 'submit', 'support', 'survey', 'update',
            'upgrade', 'url', 'user', 'valid', 'verify', 'warning',
            'webmail', 'welcome', 'wire', 'wiring',
            # Financial/Banking
            'creditcard', 'credit', 'debit', 'swift', 'iban', 'routing',
            'ach', 'wire', 'transfer', 'bitcoin', 'crypto', 'wallet',
            # Tech companies (common impersonation)
            'google', 'yahoo', 'outlook', 'gmail', 'facebook', 'twitter',
            'linkedin', 'dropbox', 'onedrive', 'icloud', 'adobe', 'zoom'
        ]
        self.shortener_domains = [
            'bit.ly', 'tinyurl.com', 'goo.gl', 'ow.ly', 'short.link',
            # PhishSage additional shorteners
            'tiny.cc', 'short.io', 'link.zip', 'is.gd', 'buff.ly',
            'adf.ly', 'rev.link', 't.me', 'u.to', 'zz.gd'
        ]
    
    def extract_features(self, url):
        """
        Extract 19 features from URL
        Returns: list of 19 numeric features (0 or 1, or normalized entropy)
        """
        features = []
        
        try:
            parsed = urllib.parse.urlparse(url)
            domain = parsed.netloc
            path = parsed.path
            
            # Feature 1: Has IP Address
            features.append(self._has_ip_address(domain))
            
            # Feature 2: Has @ Symbol
            features.append(self._has_at_symbol(url))
            
            # Feature 3: HTTPS Protocol
            features.append(self._has_https(url))
            
            # Feature 4: URL Length (>75 chars suspicious)
            features.append(self._long_url(url))
            
            # Feature 5: Number of Subdomains (>2 suspicious)
            features.append(self._excessive_subdomains(domain))
            
            # Feature 6: Has Hyphen in Domain
            features.append(self._has_hyphen_in_domain(domain))
            
            # Feature 7: Has Suspicious Keywords
            features.append(self._has_suspicious_keywords(url))
            
            # Feature 8: Has URL Shortener
            features.append(self._has_url_shortener(domain))
            
            # Feature 9: Port in URL
            features.append(self._has_non_standard_port(parsed))
            
            # Feature 10: Excess of Numbers
            features.append(self._excessive_numbers(url))
            
            # Feature 11: Domain Length
            features.append(self._long_domain(domain))
            
            # Feature 12: Multiple Dots
            features.append(self._excessive_dots(url))
            
            # Feature 13: File Extension in Domain
            features.append(self._has_file_extension(domain))
            
            # Feature 14: Suspicious TLD
            features.append(self._suspicious_tld(domain))
            
            # Feature 15: Double Slash Redirecting
            features.append(self._double_slash_redirect(url))
            
            # Feature 16: Domain Entropy (PhishSage)
            features.append(self._high_domain_entropy(domain))
            
            # Feature 17: Unicode Homograph Detection (PhishSage)
            features.append(self._has_unicode_homograph(domain))
            
            # Feature 18: Subdomain Entropy (PhishSage)
            features.append(self._high_subdomain_entropy(domain))
            
            # Feature 19: Free Email Domain (PhishSage)
            features.append(self._is_free_email_domain(domain))
            
        except Exception as e:
            print(f"Error extracting features: {e}")
            features = [0] * 19
        
        return features
    
    def _has_ip_address(self, domain):
        """Check if domain is an IP address"""
        try:
            ipaddress.ip_address(domain)
            return 1  # Suspicious
        except ValueError:
            return 0  # Legitimate
    
    def _has_at_symbol(self, url):
        """Check for @ symbol in URL"""
        return 1 if '@' in url else 0
    
    def _has_https(self, url):
        """Check if URL uses HTTPS"""
        return 0 if url.startswith('https://') else 1
    
    def _long_url(self, url):
        """Check if URL is too long (>75 chars)"""
        return 1 if len(url) > 75 else 0
    
    def _excessive_subdomains(self, domain):
        """Check for excessive subdomains"""
        subdomain_count = domain.count('.')
        return 1 if subdomain_count > 2 else 0
    
    def _has_hyphen_in_domain(self, domain):
        """Check for hyphens in domain name"""
        return 1 if '-' in domain.split('.')[0] else 0
    
    def _has_suspicious_keywords(self, url):
        """Check for suspicious keywords"""
        url_lower = url.lower()
        for keyword in self.suspicious_keywords:
            if keyword in url_lower:
                return 1
        return 0
    
    def _has_url_shortener(self, domain):
        """Check if using URL shortener service"""
        for shortener in self.shortener_domains:
            if shortener in domain.lower():
                return 1
        return 0
    
    def _has_non_standard_port(self, parsed):
        """Check for non-standard ports"""
        if parsed.port and parsed.port not in [80, 443]:
            return 1
        return 0
    
    def _excessive_numbers(self, url):
        """Check for excessive numbers"""
        numbers = re.findall(r'\d', url)
        return 1 if len(numbers) > len(url) * 0.3 else 0
    
    def _long_domain(self, domain):
        """Check if domain is unusually long"""
        return 1 if len(domain) > 30 else 0
    
    def _excessive_dots(self, url):
        """Check for excessive dots in URL"""
        return 1 if url.count('.') > 4 else 0
    
    def _has_file_extension(self, domain):
        """Check if domain has file extension"""
        extensions = ['.com', '.org', '.net', '.edu', '.gov', '.co', '.io']
        for ext in extensions:
            if domain.endswith(ext):
                return 0
        return 1
    
    def _suspicious_tld(self, domain):
        """Check for suspicious TLDs (expanded from PhishSage)"""
        suspicious_tlds = [
            '.tk', '.ml', '.ga', '.cf', '.xyz', '.top',
            # PhishSage expanded suspicious TLDs
            '.pw', '.ws', '.cc', '.cm', '.info', '.biz',
            '.download', '.loan', '.zip', '.racing', '.review',
            '.party', '.gdn', '.gb', '.space', '.su',
            '.men', '.date', '.ren', '.sk', '.click', '.work'
        ]
        for tld in suspicious_tlds:
            if domain.lower().endswith(tld):
                return 1
        return 0
    
    def _double_slash_redirect(self, url):
        """Check for redirecting by double slash"""
        if url.find('//') > 6:
            return 1
        return 0
    
    def _shannon_entropy(self, s):
        """
        Calculate Shannon entropy of a string (PhishSage feature)
        Higher entropy indicates more randomness (obfuscated/suspicious)
        """
        if not s:
            return 0.0
        
        counts = Counter(s)
        length = len(s)
        entropy = -sum((count / length) * math.log2(count / length) for count in counts.values())
        return entropy
    
    def _high_domain_entropy(self, domain):
        """
        Check if domain has high entropy (suspicious, obfuscated)
        Normalized to return 0 or 1
        """
        # Extract just the domain name part (without TLD)
        domain_parts = domain.split('.')
        if len(domain_parts) >= 2:
            domain_name = domain_parts[-2]  # Get domain before TLD
        else:
            domain_name = domain
        
        entropy = self._shannon_entropy(domain_name)
        # Threshold: entropy > 3.5 indicates suspicious randomness
        return 1 if entropy > 3.5 else 0
    
    def _has_unicode_homograph(self, domain):
        """
        Detects Unicode homoglyphs or non-ASCII characters in domain (PhishSage feature)
        Returns 1 if suspicious homoglyphs detected, 0 otherwise
        """
        # Common homoglyph substitutions (lookalike characters)
        homoglyph_map = {
            'а': 'a',  # Cyrillic 'a' looks like 'a'
            'е': 'e',  # Cyrillic 'e' looks like 'e'
            'о': 'o',  # Cyrillic 'o' looks like 'o'
            'р': 'p',  # Cyrillic 'r' looks like 'p'
            'с': 'c',  # Cyrillic 'c' looks like 'c'
            'х': 'x',  # Cyrillic 'x' looks like 'x'
            'у': 'y',  # Cyrillic 'y' looks like 'y'
            'ί': 'i',  # Greek 'i' looks like 'i'
            'Ο': 'O',  # Greek 'O' looks like 'O'
        }
        
        try:
            # Check for non-ASCII characters
            domain_lower = domain.lower()
            
            for char in domain_lower:
                if ord(char) > 127:  # Non-ASCII character
                    # Try to encode as punycode
                    try:
                        # If it can be encoded as punycode, it's suspicious
                        domain.encode('idna').decode('ascii')
                        return 1
                    except (UnicodeError, UnicodeDecodeError):
                        return 1
                
                # Check for known homoglyphs
                if char in homoglyph_map:
                    return 1
            
            return 0
        
        except Exception:
            return 0
    
    def _high_subdomain_entropy(self, domain):
        """
        Check if subdomain has high entropy (PhishSage feature)
        High entropy in subdomains is often suspicious
        """
        try:
            domain_parts = domain.split('.')
            
            # Get subdomain (all parts except domain and TLD)
            if len(domain_parts) > 2:
                # Combine all subdomain parts
                subdomain = '.'.join(domain_parts[:-2])
                
                if subdomain:
                    entropy = self._shannon_entropy(subdomain)
                    # Threshold: entropy > 3.0 indicates suspicious
                    return 1 if entropy > 3.0 else 0
            
            return 0
        
        except Exception:
            return 0
    
    def _is_free_email_domain(self, domain):
        """
        Detects if domain is a free email provider (PhishSage feature)
        Free email domains used in phishing URLs are often suspicious
        """
        free_email_domains = [
            'gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com',
            'mail.com', 'protonmail.com', 'tutanota.com',
            'yandex.com', 'qq.com', 'aol.com', 'mail.ru',
            'inbox.com', 'gmx.com', 'web.de', 'zoho.com',
            'fastmail.com', 'mailbox.org', 'laposte.net',
            'orange.fr', 'wanadoo.fr', 'sfr.fr', 'free.fr',
            'tmail.com', '10minutemail.com', 'tempmail.com',
            'guerrillamail.com', 'mailinator.com', 'throwaway.email'
        ]
        
        domain_lower = domain.lower()
        for free_domain in free_email_domains:
            if free_domain in domain_lower:
                return 1
        
        return 0
    
    def get_feature_names(self):
        """Return feature names for interpretation"""
        return [
            'has_ip_address',
            'has_at_symbol',
            'no_https',
            'long_url',
            'excessive_subdomains',
            'hyphen_in_domain',
            'suspicious_keywords',
            'url_shortener',
            'non_standard_port',
            'excessive_numbers',
            'long_domain',
            'excessive_dots',
            'file_extension_in_domain',
            'suspicious_tld',
            'double_slash_redirect',
            'high_domain_entropy',
            'unicode_homograph',
            'high_subdomain_entropy',
            'free_email_domain'
        ]
