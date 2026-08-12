"""
Amul Protein Lassi Stock Logger
---------------------------------
Checks stock status of Amul High Protein Plain Lassi and Rose Lassi
on shop.amul.com, and records the date/time whenever a product is found in stock.

No email/Telegram needed -- results are printed to the screen and saved
to amul_lassi_log.txt in the same folder as this script.

SETUP:
1. Install dependency:  pip install requests
2. Run manually to test:  python amul_lassi_logger.py
3. To monitor "the whole day", schedule it (pick one):
   - Linux/Mac cron (every 10 min):
       */10 * * * * /usr/bin/python3 /path/to/amul_lassi_logger.py
   - Windows Task Scheduler: run every 10 min.
   - Or run continuously in one terminal window:
       python amul_lassi_logger.py --loop
"""

import os
import re
import time
import argparse
import requests

PRODUCTS = {
    "Plain Lassi": "https://shop.amul.com/en/product/amul-high-protein-plain-lassi-200-ml-or-pack-of-30",
    "Rose Lassi": "https://shop.amul.com/en/product/amul-high-protein-rose-lassi-200-ml-or-pack-of-30",
}

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "amul_lassi_log.txt")
CHECK_INTERVAL_SECONDS = 600  # used only with --loop (10 minutes)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/125.0 Safari/537.36"
}


def get_stock_status(url: str) -> str:
    """Returns 'in_stock', 'out_of_stock', or 'unknown'."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"[ERROR] Fetching {url} failed: {e}")
        return "unknown"

    html = resp.text

    if re.search(r"sold\s*out", html, re.IGNORECASE) or re.search(r"notify\s*me", html, re.IGNORECASE):
        return "out_of_stock"

    if re.search(r"add\s*to\s*cart", html, re.IGNORECASE) or re.search(r"\bADD\b", html):
        return "in_stock"

    return "unknown"


def log_line(text: str):
    print(text)
    with open(LOG_FILE, "a") as f:
        f.write(text + "\n")


def check_once():
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    for name, url in PRODUCTS.items():
        status = get_stock_status(url)
        if status == "in_stock":
            log_line(f"[{timestamp}] ✅ {name} was IN STOCK")
        elif status == "out_of_stock":
            print(f"[{timestamp}] {name}: out of stock")
        else:
            print(f"[{timestamp}] {name}: status unknown")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--loop", action="store_true",
                         help="Run continuously, checking every CHECK_INTERVAL_SECONDS")
    args = parser.parse_args()

    if args.loop:
        print(f"Starting continuous monitor (every {CHECK_INTERVAL_SECONDS}s). Ctrl+C to stop.")
        while True:
            check_once()
            time.sleep(CHECK_INTERVAL_SECONDS)
    else:
        check_once()


if __name__ == "__main__":
    main()
