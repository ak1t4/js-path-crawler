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

def main(base_url):
    print(f"Fetching .js URLs from {base_url}...")
    js_urls = extract_js_urls(base_url)
    print(f"Found {len(js_urls)} .js files:")
    for js_url in js_urls:
        print(js_url)

    print("\nExtracting paths from .js files...")
    all_paths = set()
    for js_url in js_urls:
        paths = extract_paths_from_js(js_url)
        all_paths.update(paths)

    print(f"\nFound {len(all_paths)} unique paths:")
    for path in sorted(all_paths):
        print(path)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python3 crawl.py <url>")
    else:
        main(sys.argv[1])
