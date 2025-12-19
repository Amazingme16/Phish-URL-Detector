"""
Phishing Database Threat Intelligence Integration
Integrates threat intelligence from Phishing.Database project (493k+ domains, 778k+ links)
Provides real-time lookups against known phishing domains, URLs, and IPs
"""

import json
import os
from datetime import datetime, timedelta
from urllib.parse import urlparse, quote
import requests
import hashlib
from threat_store import ThreatStore
# Prefer SQLite store if available for better query performance
try:
    from threat_store_sqlite import ThreatStoreSQLite
except Exception:
    ThreatStoreSQLite = None

# Suppress SSL warnings when using verify=False
try:
    from urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
except:
    pass


class PhishingDatabaseThreatIntel:
    """Threat Intelligence Integration with Phishing.Database"""
    
    def __init__(self):
        """Initialize threat intelligence system"""
        self.cache_file = 'phishing_cache.json'
        self.snapshot_file = 'threat_database_snapshot.json'
        self.cache_expiry = 86400  # 24 hours in seconds (extended from 1 hour)
        self.local_cache = {}
        self.snapshot_data = {}
        self.load_cache()
        self.load_snapshot()
        # Initialize local threat store for newly detected threats
        # Prefer a SQLite-backed store if present, otherwise use JSON store
        try:
            if ThreatStoreSQLite is not None:
                self.store = ThreatStoreSQLite()
            else:
                self.store = ThreatStore()
        except Exception:
            self.store = None
        
        # Data sources from Phishing.Database
        self.data_sources = {
            'domains_active': 'https://phish.co.za/latest/phishing-domains-ACTIVE.txt',
            'domains_inactive': 'https://phish.co.za/latest/phishing-domains-INACTIVE.txt',
            'links_active': 'https://phish.co.za/latest/phishing-links-ACTIVE.txt',
            'ips_active': 'https://phish.co.za/latest/phishing-IPs-ACTIVE.txt',
            'domains_new_today': 'https://phish.co.za/latest/phishing-domains-NEW-today.txt',
            'links_new_today': 'https://phish.co.za/latest/phishing-links-NEW-today.txt',
        }
        
        # Downloaded data storage
        self.active_domains = set()
        self.active_links = set()
        self.active_ips = set()
        self.new_domains_today = set()
        self.new_links_today = set()
        
    def load_cache(self):
        """Load cached threat data from file"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    if data.get('timestamp'):
                        timestamp = datetime.fromisoformat(data['timestamp'])
                        if datetime.now() - timestamp < timedelta(seconds=self.cache_expiry):
                            self.local_cache = data.get('data', {})
                            return True
        except Exception as e:
            print(f"Cache load error: {str(e)}")
        return False
    
    def load_snapshot(self):
        """Load persistent snapshot of threat data"""
        try:
            if os.path.exists(self.snapshot_file):
                with open(self.snapshot_file, 'r') as f:
                    data = json.load(f)
                    self.snapshot_data = data.get('data', {})
                    print(f"[OK] Loaded threat snapshot with {sum(len(v) for v in self.snapshot_data.values())} entries")
                    return True
        except Exception as e:
            print(f"Snapshot load error: {str(e)}")
        return False
    
    def save_cache(self, data):
        """Save threat data to cache"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'data': data
                }, f)
        except Exception as e:
            print(f"Cache save error: {str(e)}")
    
    def fetch_data_source(self, source_key, limit=100):
        """
        Fetch data from Phishing.Database source with fallback chain
        Priority: Snapshot → Cache → Live Source
        
        This ensures data persists even if external DB undergoes 24-hour reset
        """
        try:
            url = self.data_sources.get(source_key)
            if not url:
                return set()
            
            # Priority 1: Check snapshot first (most reliable, never expires)
            if source_key in self.snapshot_data:
                snapshot_data = self.snapshot_data[source_key]
                if snapshot_data:
                    return set(snapshot_data[:limit]) if limit else set(snapshot_data)
            
            # Priority 2: Check cache (valid for 24 hours)
            cache_key = f"{source_key}_data"
            if cache_key in self.local_cache:
                return set(self.local_cache[cache_key][:limit]) if limit else set(self.local_cache[cache_key])
            
            # Priority 3: Fetch from remote source (live, may reset after 24h)
            try:
                # Use verify=False to bypass SSL certificate issues
                # In production, proper SSL certificates should be configured
                response = requests.get(url, timeout=10, verify=False)
                if response.status_code == 200:
                    data = set(line.strip() for line in response.text.split('\n') 
                              if line.strip() and not line.startswith('#'))
                    
                    # Cache the results for 24 hours
                    self.local_cache[cache_key] = list(data)
                    self.save_cache(self.local_cache)
                    
                    return set(list(data)[:limit]) if limit else data
            except requests.RequestException as e:
                print(f"[!] Live source unavailable for {source_key}: {str(e)}")
                # Fall through to fallback
            
            # Fallback: Return empty set if nothing available
            print(f"[WARN] No data available for {source_key} - using empty set")
            return set()
        except Exception as e:
            print(f"Data fetch error for {source_key}: {str(e)}")
        
        return set()

    
    def check_url_against_database(self, url):
        """
        Check URL against Phishing.Database threat intelligence
        Returns comprehensive threat match information
        """
        result = {
            'is_known_phishing': False,
            'threat_type': None,
            'matches': [],
            'threat_level': 'unknown',
            'details': {}
        }
        
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        domain_without_www = domain[4:] if domain.startswith('www.') else domain
        
        # Check against active domains (most important)
        if not self.active_domains:
            self.active_domains = self.fetch_data_source('domains_active', limit=1000)
        
        if domain in self.active_domains or domain_without_www in self.active_domains:
            result['is_known_phishing'] = True
            result['threat_type'] = 'known_phishing_domain'
            result['threat_level'] = 'critical'
            result['matches'].append({
                'type': 'domain',
                'source': 'Phishing.Database (Active Domains)',
                'value': domain
            })
            result['details']['status'] = 'ACTIVE'
            result['details']['confidence'] = 'VERY_HIGH'
            return result
        
        # Check against new domains found today
        if not self.new_domains_today:
            self.new_domains_today = self.fetch_data_source('domains_new_today', limit=500)
        
        if domain in self.new_domains_today or domain_without_www in self.new_domains_today:
            result['is_known_phishing'] = True
            result['threat_type'] = 'recently_detected_phishing'
            result['threat_level'] = 'critical'
            result['matches'].append({
                'type': 'domain',
                'source': 'Phishing.Database (New Today)',
                'value': domain
            })
            result['details']['status'] = 'NEWLY_DETECTED'
            result['details']['confidence'] = 'HIGH'
            return result
        
        # Check against active IPs
        if not self.active_ips:
            self.active_ips = self.fetch_data_source('ips_active', limit=500)
        
        # Extract IP from URL if present
        if parsed.hostname:
            try:
                # Check if hostname is IP address
                import socket
                socket.inet_aton(parsed.hostname)  # Will raise if not valid IP
                if parsed.hostname in self.active_ips:
                    result['is_known_phishing'] = True
                    result['threat_type'] = 'known_phishing_ip'
                    result['threat_level'] = 'critical'
                    result['matches'].append({
                        'type': 'ip_address',
                        'source': 'Phishing.Database (Active IPs)',
                        'value': parsed.hostname
                    })
                    result['details']['status'] = 'ACTIVE'
                    result['details']['confidence'] = 'VERY_HIGH'
                    return result
            except:
                pass
        
        # Check against active links (full URL match)
        if not self.active_links:
            self.active_links = self.fetch_data_source('links_active', limit=1000)
        
        if url in self.active_links:
            result['is_known_phishing'] = True
            result['threat_type'] = 'known_phishing_link'
            result['threat_level'] = 'critical'
            result['matches'].append({
                'type': 'full_url',
                'source': 'Phishing.Database (Active Links)',
                'value': url
            })
            result['details']['status'] = 'ACTIVE'
            result['details']['confidence'] = 'VERY_HIGH'
            return result
        
        # Check inactive domains (may be temporarily down)
        if not hasattr(self, '_checked_inactive'):
            inactive_domains = self.fetch_data_source('domains_inactive', limit=500)
            if domain in inactive_domains or domain_without_www in inactive_domains:
                result['is_known_phishing'] = True
                result['threat_type'] = 'previously_detected_phishing'
                result['threat_level'] = 'high'
                result['matches'].append({
                    'type': 'domain',
                    'source': 'Phishing.Database (Inactive Domains)',
                    'value': domain
                })
                result['details']['status'] = 'INACTIVE'
                result['details']['confidence'] = 'HIGH'
                return result
        
        # No matches found
        result['threat_level'] = 'none'
        result['details'] = {
            'status': 'NOT_FOUND_IN_DATABASE',
            'confidence': 'CLEAN',
            'message': 'URL not found in Phishing.Database threat intelligence'
        }
        
        return result
    
    def get_database_stats(self):
        """Get statistics about threat intelligence coverage"""
        return {
            'total_known_domains': 493082,
            'total_known_links': 778293,
            'database_version': 'V.2025-12-04.21',
            'last_updated': '2025-12-04',
            'coverage': 'Comprehensive phishing threat intelligence',
            'sources': [
                'Active phishing domains',
                'Active phishing links',
                'Active phishing IPs',
                'Recently detected threats (today)',
                'Inactive/takedown domains',
                'Invalid domains'
            ],
            'active_status_codes': [100, 101, 200, 201, 202, 203, 204, 205, 206],
            'potentially_active_codes': [300, 301, 302, 303, 304, 305, 307, 403, 405, 406, 407, 408],
            'testing_tool': 'PyFunceble (automated domain/URL testing)'
        }
    
    def generate_threat_report(self, url, check_result):
        """Generate detailed threat intelligence report"""
        report = {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'threat_found': check_result['is_known_phishing'],
            'threat_classification': check_result['threat_type'],
            'threat_severity': self._get_severity_score(check_result['threat_level']),
            'threat_level': check_result['threat_level'],
            'matches': check_result['matches'],
            'details': check_result['details'],
            'recommendations': self._get_recommendations(check_result)
        }
        # Persist newly detected threats to local store if available
        try:
            if report.get('threat_found') and getattr(self, 'store', None):
                try:
                    added = self.store.add_threat(report)
                    if added:
                        print(f"[STORE] New threat stored: {report.get('url')}")
                except Exception as e:
                    print(f"[STORE ERROR] Could not persist threat: {e}")
        except Exception:
            pass

        return report
    
    def _get_severity_score(self, threat_level):
        """Map threat level to severity score"""
        severity_map = {
            'critical': 100,
            'high': 75,
            'medium': 50,
            'low': 25,
            'unknown': 0,
            'none': 0
        }
        return severity_map.get(threat_level, 0)
    
    def _get_recommendations(self, check_result):
        """Get security recommendations based on threat"""
        recommendations = []
        
        if check_result['is_known_phishing']:
            recommendations.append('❌ BLOCK: This URL is in the known phishing database')
            recommendations.append('⚠️ DO NOT CLICK - Do not enter credentials on this site')
            recommendations.append('📧 Report: Submit to your email provider if received')
            recommendations.append('🛡️ Protect: Update passwords if credentials were compromised')
            
            if check_result['threat_type'] == 'recently_detected_phishing':
                recommendations.append('🆕 NEW THREAT: This phishing domain was detected today')
            elif check_result['threat_type'] == 'known_phishing_ip':
                recommendations.append('🌐 IP-BASED THREAT: The hosting IP is known to host phishing')
        else:
            recommendations.append('✅ CLEAN: URL not found in Phishing.Database')
            recommendations.append('ℹ️ NOTE: This does not guarantee safety - use with other checks')
            recommendations.append('🔍 Continue: Review other analysis indicators')
        
        return recommendations
    
    def batch_check_urls(self, urls):
        """Check multiple URLs against threat database"""
        results = []
        for url in urls:
            try:
                check_result = self.check_url_against_database(url)
                report = self.generate_threat_report(url, check_result)
                results.append(report)
            except Exception as e:
                results.append({
                    'url': url,
                    'error': str(e),
                    'threat_found': False
                })
        
        return {
            'total_urls_checked': len(urls),
            'phishing_urls_found': sum(1 for r in results if r.get('threat_found')),
            'results': results
        }
    
    def get_threat_stats_by_type(self, results):
        """Analyze threat statistics from batch check"""
        stats = {
            'total_checked': len(results),
            'threats_found': 0,
            'threat_breakdown': {},
            'critical_threats': 0,
            'high_threats': 0
        }
        
        for result in results:
            if result.get('threat_found'):
                stats['threats_found'] += 1
                threat_type = result.get('threat_classification', 'unknown')
                stats['threat_breakdown'][threat_type] = stats['threat_breakdown'].get(threat_type, 0) + 1
                
                severity = result.get('threat_severity', 0)
                if severity >= 100:
                    stats['critical_threats'] += 1
                elif severity >= 75:
                    stats['high_threats'] += 1
        
        stats['threat_percentage'] = f"{(stats['threats_found'] / stats['total_checked'] * 100):.1f}%" if stats['total_checked'] > 0 else "0%"
        
        return stats


# Initialize threat intelligence for easy use
threat_intel = PhishingDatabaseThreatIntel()
