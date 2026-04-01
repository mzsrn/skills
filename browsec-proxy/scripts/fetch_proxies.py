#!/usr/bin/env python3
"""
fetch_proxies.py — Fetch and validate HTTPS proxies from the Browsec API.

Usage:
    python3 fetch_proxies.py [--country XX] [--limit N] [--validate] [--json] [--free-only]

The API returns random servers on each call. Free-tier servers use port 443;
premium servers use non-standard ports.
"""

import argparse
import json
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

API_URL = "https://browsec.com/api/v1/servers?uc=ru&stdomains=1"


def fetch_servers() -> dict:
    """Fetch the full server list from the Browsec API."""
    req = urllib.request.Request(API_URL, method="GET")
    req.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except Exception as exc:
        print(f"Failed to fetch servers: {exc}", file=sys.stderr)
        sys.exit(1)


def extract_proxies(data: dict, country: str | None = None) -> list[dict]:
    """Extract free-tier proxy entries from the API response.

    Only uses 'servers' (free). Premium servers require auth (not yet supported).
    Each proxy dict: {"host", "port", "country"}
    """
    countries = data.get("countries", {})
    proxies = []

    for cc, info in countries.items():
        if country and cc.lower() != country.lower():
            continue

        for srv in info.get("servers", []):
            proxies.append({
                "host": srv["host"],
                "port": srv["port"],
                "country": cc.upper(),
            })

    return proxies


def check_proxy(proxy: dict, timeout: float = 10.0) -> bool:
    """Verify proxy forwards traffic by making an HTTP request through it."""
    host, port = proxy["host"], proxy["port"]
    proxy_url = f"https://{host}:{port}"
    handler = urllib.request.ProxyHandler({"http": proxy_url})
    opener = urllib.request.build_opener(handler)
    try:
        resp = opener.open("http://httpbin.org/ip", timeout=timeout)
        return resp.status == 200
    except Exception:
        return False


def validate_proxies(proxies: list[dict], timeout: float = 10.0) -> list[dict]:
    """Return only proxies that actually forward requests."""
    if not proxies:
        return []
    alive = []
    with ThreadPoolExecutor(max_workers=min(len(proxies), 20)) as pool:
        futures = {pool.submit(check_proxy, p, timeout): p for p in proxies}
        for fut in as_completed(futures):
            if fut.result():
                alive.append(futures[fut])
    return alive


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch HTTPS proxies from Browsec")
    parser.add_argument("--country", default=None, help="Country code (e.g. US, DE, NL)")
    parser.add_argument("--limit", type=int, default=0, help="Max proxies to return (0 = all)")
    parser.add_argument("--validate", action="store_true", help="Only return working proxies")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    data = fetch_servers()
    proxies = extract_proxies(data, args.country)

    if not proxies:
        print("No proxies found.", file=sys.stderr)
        sys.exit(1)

    if args.validate:
        proxies = validate_proxies(proxies)
        if not proxies:
            print("All proxies failed validation.", file=sys.stderr)
            sys.exit(1)

    if args.limit > 0:
        proxies = proxies[:args.limit]

    if args.json:
        print(json.dumps(proxies, indent=2))
    else:
        print(f"{'HOST':<40} {'PORT':<8} {'COUNTRY':<8}")
        print("-" * 56)
        for p in proxies:
            print(f"{p['host']:<40} {p['port']:<8} {p['country']:<8}")
        print(f"\nTotal: {len(proxies)}")


if __name__ == "__main__":
    main()
