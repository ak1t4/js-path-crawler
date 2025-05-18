# 🕷️ JS Path Crawler

A simple Python script to extract JavaScript file URLs from a given webpage, and then scan those JS files to find internal API paths or route definitions.

## 📌 Features

- Automatically parses the HTML to find linked `.js` files.
- Crawls the `.js` files to extract path patterns like `/api/v1/...`, `/admin/login`, etc.
- Useful for bug bounty, penetration testing, and web application mapping.

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

## Example Output

Here is a screenshot showing the script running successfully:

![Terminal output](./images/terminal-output.png)

## ⚠️ Notes

- The script disables SSL certificate verification by default to avoid issues with expired or self-signed certificates.
- Paths are extracted using basic regular expressions and might include false positives. Review the output manually for best results.

## 📂 Output

- Prints a list of all `.js` files found.
- Extracted internal paths from those files.

## 👨‍💻 Author

Created by a fellow security researcher.

---

✅ Happy hunting!
