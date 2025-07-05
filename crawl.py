import requests
import re
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def extract_js_urls(base_url):
    js_urls = set()
    try:
        response = requests.get(base_url, verify=False, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        for script in soup.find_all('script', src=True):
            src = script['src']
            if src.endswith('.js'):
                full_url = urljoin(base_url, src)
                js_urls.add(full_url)
    except requests.RequestException as e:
        print(f"Error while fetching .js URLs: {e}")
    return list(js_urls)

def extract_paths_from_js(js_url):
    paths = set()
    try:
        response = requests.get(js_url, verify=False, timeout=10)
        response.raise_for_status()
        content = response.text
        found = re.findall(r'(/[\w\-/\.?=]+)', content)
        for path in found:
            if len(path) > 1 and not path.startswith('//'):
                paths.add(path)
    except requests.RequestException as e:
        print(f"Error while reading JS file {js_url}: {e}")
    return paths

def extract_sensitive_tokens_from_js(js_url):
    """Extract sensitive tokens like API keys, secrets, passwords from JS files."""
    sensitive_tokens = set()
    try:
        response = requests.get(js_url, verify=False, timeout=10)
        response.raise_for_status()
        content = response.text
        
        # Define patterns for sensitive tokens
        patterns = {
            'API Keys': [
                r'["\']api[_-]?key["\'][\s]*[:=][\s]*["\']([A-Za-z0-9\-_]{16,})["\']',
                r'["\']apikey["\'][\s]*[:=][\s]*["\']([A-Za-z0-9\-_]{16,})["\']',
                r'["\']key["\'][\s]*[:=][\s]*["\']([A-Za-z0-9\-_]{16,})["\']'
            ],
            'AWS Keys': [
                r'AKIA[0-9A-Z]{16}',  # AWS Access Key ID
                r'["\']aws[_-]?access[_-]?key[_-]?id["\'][\s]*[:=][\s]*["\']([A-Za-z0-9\-_]{16,})["\']',
                r'["\']aws[_-]?secret[_-]?access[_-]?key["\'][\s]*[:=][\s]*["\']([A-Za-z0-9\-_/+=]{40})["\']'
            ],
            'Tokens': [
                r'["\']token["\'][\s]*[:=][\s]*["\']([A-Za-z0-9\-_\.]{20,})["\']',
                r'["\']auth[_-]?token["\'][\s]*[:=][\s]*["\']([A-Za-z0-9\-_\.]{20,})["\']',
                r'["\']access[_-]?token["\'][\s]*[:=][\s]*["\']([A-Za-z0-9\-_\.]{20,})["\']',
                r'Bearer[\s]+([A-Za-z0-9\-_\.]{20,})'
            ],
            'JWT Tokens': [
                r'eyJ[A-Za-z0-9\-_=]+\.eyJ[A-Za-z0-9\-_=]+\.[A-Za-z0-9\-_.+/=]*'  # JWT pattern
            ],
            'Secrets': [
                r'["\']secret["\'][\s]*[:=][\s]*["\']([A-Za-z0-9\-_]{16,})["\']',
                r'["\']client[_-]?secret["\'][\s]*[:=][\s]*["\']([A-Za-z0-9\-_]{16,})["\']',
                r'["\']app[_-]?secret["\'][\s]*[:=][\s]*["\']([A-Za-z0-9\-_]{16,})["\']'
            ],
            'Passwords': [
                r'["\']password["\'][\s]*[:=][\s]*["\']([^"\']{6,})["\']',
                r'["\']pass["\'][\s]*[:=][\s]*["\']([^"\']{6,})["\']',
                r'["\']pwd["\'][\s]*[:=][\s]*["\']([^"\']{6,})["\']'
            ],
            'Database Connections': [
                r'mongodb://[^\s"\']*',
                r'mysql://[^\s"\']*',
                r'postgres://[^\s"\']*',
                r'["\']database[_-]?url["\'][\s]*[:=][\s]*["\']([^"\']+)["\']',
                r'["\']db[_-]?connection["\'][\s]*[:=][\s]*["\']([^"\']+)["\']'
            ],
            'Google API Keys': [
                r'AIza[0-9A-Za-z\\-_]{35}'  # Google API Key
            ],
            'GitHub Tokens': [
                r'ghp_[A-Za-z0-9]{36}',  # GitHub Personal Access Token
                r'gho_[A-Za-z0-9]{36}',  # GitHub OAuth Token
                r'ghu_[A-Za-z0-9]{36}',  # GitHub User-to-server Token
                r'ghs_[A-Za-z0-9]{36}',  # GitHub Server-to-server Token
                r'ghr_[A-Za-z0-9]{36}'   # GitHub Refresh Token
            ],
            'Private Keys': [
                r'-----BEGIN[A-Z\s]+PRIVATE KEY-----[A-Za-z0-9\s/+=\n]+-----END[A-Z\s]+PRIVATE KEY-----'
            ]
        }
        
        for category, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        match = match[0] if match[0] else match[-1]
                    if len(match) > 5:  # Filter out very short matches
                        sensitive_tokens.add(f"[{category}] {match}")
        
        # Also look for common variable names that might contain sensitive data
        variable_patterns = [
            r'(?:const|let|var)\s+(\w*(?:key|secret|token|password|pass|pwd|api)\w*)\s*=\s*["\']([^"\']{8,})["\']',
            r'(\w*(?:key|secret|token|password|pass|pwd|api)\w*)\s*:\s*["\']([^"\']{8,})["\']'
        ]
        
        for pattern in variable_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for var_name, value in matches:
                if len(value) > 7:  # Filter out short values
                    sensitive_tokens.add(f"[Variable] {var_name} = {value}")
                    
    except requests.RequestException as e:
        print(f"Error while reading JS file for tokens {js_url}: {e}")
    
    return sensitive_tokens

def main(base_url):
    print(f"Fetching .js URLs from {base_url}...")
    js_urls = extract_js_urls(base_url)
    print(f"Found {len(js_urls)} .js files:")
    for js_url in js_urls:
        print(js_url)

    print("\nExtracting paths from .js files...")
    all_paths = set()
    all_sensitive_tokens = set()
    
    for js_url in js_urls:
        print(f"\nScanning {js_url}...")
        
        # Extract paths
        paths = extract_paths_from_js(js_url)
        all_paths.update(paths)
        
        # Extract sensitive tokens
        sensitive_tokens = extract_sensitive_tokens_from_js(js_url)
        all_sensitive_tokens.update(sensitive_tokens)
        
        if sensitive_tokens:
            print(f"  🚨 Found {len(sensitive_tokens)} sensitive tokens in this file:")
            for token in sorted(sensitive_tokens):
                print(f"    {token}")

    print(f"\n📍 Found {len(all_paths)} unique paths:")
    for path in sorted(all_paths):
        print(f"  {path}")
        
    print(f"\n🔐 Found {len(all_sensitive_tokens)} total sensitive tokens:")
    if all_sensitive_tokens:
        for token in sorted(all_sensitive_tokens):
            print(f"  {token}")
    else:
        print("  No sensitive tokens found.")
        
    # Summary
    print(f"\n📊 SUMMARY:")
    print(f"  - JavaScript files scanned: {len(js_urls)}")
    print(f"  - API paths discovered: {len(all_paths)}")
    print(f"  - Sensitive tokens found: {len(all_sensitive_tokens)}")
    
    if all_sensitive_tokens:
        print(f"\n⚠️  WARNING: Sensitive tokens were found! Review these carefully for security issues.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python3 crawl.py <url>")
    else:
        main(sys.argv[1])
