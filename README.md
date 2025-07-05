# 🕷️ JS Path Crawler

A simple Python script to extract JavaScript file URLs from a given webpage, and then scan those JS files to find internal API paths or route definitions.

## 📌 Features

- Automatically parses the HTML to find linked `.js` files.
- Crawls the `.js` files to extract path patterns like `/api/v1/...`, `/admin/login`, etc.
- **🔐 NEW: Scans JavaScript files for sensitive tokens including:**
  - API keys and secrets
  - AWS credentials
  - JWT tokens
  - Database connection strings
  - GitHub tokens
  - Private keys
  - Passwords and authentication tokens
- Useful for bug bounty, penetration testing, and web application security assessment.

## 🚀 Requirements

- Python 3.x
- pip

Install the dependencies:

```bash
pip install -r requirements.txt
```

## 🛠️ Usage

```bash
python3 crawl.py <target_url>
```

### Example:

```bash
python3 crawl.py https://example.com
```

### Testing on vulnerable applications:

```bash
python3 crawl.py https://testphp.vulnweb.com
```

This will scan the vulnerable test application for JavaScript files and extract both API paths and sensitive tokens that might be exposed.

## Example Output

Here is a screenshot showing the script running successfully:

![Terminal output](terminal-output.png)

### Sample Output with Sensitive Token Detection:

```
Fetching .js URLs from https://example.com...
Found 2 .js files:
https://example.com/assets/app.js
https://example.com/config.js

Extracting paths from .js files...

Scanning https://example.com/config.js...
  🚨 Found 2 sensitive tokens in this file:
    [AWS Keys] AKIAIOSFODNN7EXAMPLE
    [Variable] api_key = sk-1234567890abcdef

📍 Found 5 unique paths:
  /api/v1/users
  /api/admin
  /auth/login

🔐 Found 2 total sensitive tokens:
  [AWS Keys] AKIAIOSFODNN7EXAMPLE
  [Variable] api_key = sk-1234567890abcdef

📊 SUMMARY:
  - JavaScript files scanned: 2
  - API paths discovered: 5
  - Sensitive tokens found: 2

⚠️  WARNING: Sensitive tokens were found! Review these carefully for security issues.
```

## ⚠️ Notes

- The script disables SSL certificate verification by default to avoid issues with expired or self-signed certificates.
- Paths are extracted using basic regular expressions and might include false positives. Review the output manually for best results.

## 📂 Output

- Prints a list of all `.js` files found.
- Extracted internal paths from those files.
- **🔐 NEW: Lists sensitive tokens found in JavaScript files with categorization.**
- Provides a summary of findings including security warnings.

## 👨‍💻 Author

Created by a fellow security researcher.

---

✅ Happy hunting!
