# IndexSearcher

A Python-based graphical web enumeration tool designed for **authorized security testing**.  
This application helps identify common entry points such as `index.html`, admin panels, and WordPress endpoints on a target website using a configurable wordlist and realistic HTTP behavior.

---

## ⚠️ Legal & Ethical Disclaimer

This tool **must only be used on webpages you own or have explicit permission to test**.  
Unauthorized scanning or enumeration of third-party systems may be illegal in your jurisdiction.  
I assume no responsibility for misuse.

---

## Features

- **A GUI**
  - Simple and easy to understand.
  - No external GUI frameworks required

- **Admin Panel /Index.html Discovery**
  - Generic website paths
  - WordPress-specific endpoints
  - Custom wordlist support

- **WordPress Detection**
  - Passive detection using common WP paths
  - Automatically expands enumeration when detected

- **Status Code Filtering**
  - Only `200`
  - `200 + 403`
  - `200, 301, 302, 403`

- **User-Agent Simulation**
  - Normal browser user
  - Admin-like user agent

- **Rate Limiting**
  - Control requests per second
  - Helps avoid detection or server overload

- **Proxy Support**
  - Burp Suite
  - Tor (SOCKS5)
  - Any HTTP/S proxy

- **Export Results**
  - TXT
  - JSON

---

## Overview

- Target configuration panel
- Live scan output
- Exportable result list

---

## Requirements

- Python **3.8+**
- `requests` library

Install dependencies:

```bash
pip install requests

