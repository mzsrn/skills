---
name: browsec-proxy
description: >
  Fetch working HTTPS proxies from the Browsec API and use them to route
  requests through specific countries. Trigger when the agent needs to: access
  geo-restricted content, get localized pricing, compare prices across regions,
  route traffic through a country, bypass geo-blocking, check regional
  availability, book travel/hotels at local prices, access region-locked APIs,
  or scrape geo-dependent data. Also trigger on keywords: "proxy", "VPN",
  "geo", "localized price", "country IP", "blocked", "region", "travel prices".
---

# Proxy Fetch

Fetch and validate HTTPS proxies from the Browsec VPN API so agents can route
requests through specific countries.

## Use cases

- **Geo-blocked content** — access websites, APIs, and services restricted to
  specific countries (streaming catalogs, news sites, government portals).
- **Subscription & SaaS pricing** — compare prices for software, cloud services,
  and subscriptions across regions (often 2-5x cheaper in developing countries).
- **Travel & booking** — find cheaper flights, hotels, and car rentals by
  searching from different countries (prices vary heavily by origin).
- **Regional availability** — check if a product, service, or feature is
  available in a specific market before launch or expansion.
- **App store prices** — compare mobile app and in-app purchase pricing across
  App Store / Google Play regions.
- **Ad & SEO verification** — see what ads are shown, what search results look
  like, or how a landing page renders in a target market.
- **E-commerce price arbitrage** — find the cheapest region for electronics,
  software licenses, gift cards, or digital goods.
- **Compliance & localization QA** — verify that geo-targeting, language
  redirects, cookie banners, and legal disclaimers work correctly per region.
- **Market research** — scrape localized product catalogs, competitor pricing,
  and regional promotions without being blocked.

## API

The proxy list is available at:

```
https://browsec.com/api/v1/servers?uc=ru&stdomains=1
```

The server returns **random** addresses on each call. Response structure:

```json
{
  "countries": {
    "us": {
      "servers": [
        {"host": "us31.swiftcdn.org", "port": 6375}
      ],
      "premium_servers": [
        {"host": "us205.speedycdn.space", "port": 11913}
      ]
    }
  },
  "recommended_countries": {
    "free": ["de", "lv", "lt"],
    "premium": ["at", "de", "fi", "nl", "us", ...]
  }
}
```

- `servers` — free tier (typically port 443), **use these**
- `premium_servers` — premium tier (requires auth, not yet supported)
- Proxies are **HTTPS proxies** — connection to proxy via TLS
- Support both `http://` targets (fast, forward proxy) and `https://` targets
  (CONNECT tunnel, slower)

## Finding a working proxy

**Important:** These are free community proxies — they are slow. Finding and
validating a working proxy may take 1-2 minutes. Inform the user that the
search is in progress and ask them to be patient.

Proxies go up and down. The agent MUST validate before use:

### Using the helper script

The script is at `scripts/fetch_proxies.py` relative to the plugin root
(two levels up from this SKILL.md's base directory).

```bash
# Find a working proxy in any country
python3 {base_dir}/../../scripts/fetch_proxies.py --validate --limit 1 --json

# Find a working German proxy
python3 {base_dir}/../../scripts/fetch_proxies.py --country DE --validate --json

# List all available proxies
python3 {base_dir}/../../scripts/fetch_proxies.py
```

Replace `{base_dir}` with the "Base directory for this skill" path shown when
this skill is loaded.

### Validation logic (for inline use)

```python
import json
import urllib.request

API_URL = "https://browsec.com/api/v1/servers?uc=ru&stdomains=1"

# 1. Fetch proxy list
data = json.loads(urllib.request.urlopen(API_URL, timeout=15).read())

# 2. Collect proxies for a country (e.g. "nl")
country = data["countries"].get("nl", {})
servers = country.get("servers", [])  # free tier only

# 3. Find first working proxy by making a real HTTP request through it
def is_alive(host, port, timeout=10):
    proxy_url = f"https://{host}:{port}"
    handler = urllib.request.ProxyHandler({"http": proxy_url})
    opener = urllib.request.build_opener(handler)
    try:
        return opener.open("http://httpbin.org/ip", timeout=timeout).status == 200
    except Exception:
        return False

working = None
for srv in servers:
    if is_alive(srv["host"], srv["port"]):
        working = srv
        break
```

## Using a proxy

```python
import urllib.request

proxy_url = f"https://{working['host']}:{working['port']}"
handler = urllib.request.ProxyHandler({"https": proxy_url})
opener = urllib.request.build_opener(handler)

resp = opener.open("https://example.com", timeout=15)
```

With curl:
```bash
curl -x https://host:port https://example.com
```

## Rotation strategy

1. Fetch several proxies for the target country.
2. Validate each one (TLS handshake).
3. Use the first working proxy.
4. On failure mid-request, try the next one.
5. If all fail, re-fetch (the API returns random servers each time) and retry.
6. If still failing, inform the user.

## Countries with free servers

The API typically provides free servers for: **DE, LT, LV, NL, SG, UK, US**.
All other countries usually require premium tier.

## Error handling

- **Connection timeout on fetch** — retry once, then report.
- **No proxies for country** — suggest nearby country or re-fetch.
- **All proxies dead** — re-fetch (random rotation) and try again.
