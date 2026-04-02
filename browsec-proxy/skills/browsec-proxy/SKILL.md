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

## Agent behavior

**Do NOT explain the proxy-fetching process to the user.** Fetch and validate
proxies silently as an internal step. The user should only see the final result
of the task they asked for (e.g. localized prices, geo-restricted content),
not the proxy plumbing. Before starting validation, warn the user once:
"These are free Browsec proxies — they can be slow. This may take 1-2
minutes." Then stay silent until you have results.

**Do NOT use WebFetch, Fetch, or raw curl commands. Do NOT call any API URLs
directly. ALL operations go through the bundled `fetch_proxies.sh` script —
it handles API calls, validation, and proxied requests internally.**

**Do NOT pipe script output into python3, jq, node, or any other tool.
You are an LLM — read the JSON output yourself and extract what you need.
This rule applies to ALL calls including retries. Never fall back to python
or other tools even when previous attempts fail.**

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

## How to use

Replace `{base_dir}` with the base directory path shown when this skill is
loaded. The script path includes `../../` to reach the plugin root from there.

### Step 1 — Get the proxy list

```bash
bash {base_dir}/../../scripts/fetch_proxies.sh --list
```

Returns raw JSON with all countries. Parse it yourself — extract `host` and
`port` from the `"servers"` arrays for the country you need (free tier).
Skip `"premium_servers"` (requires auth).

### Step 2 — Validate and fetch

Pass extracted host:port pairs to the script to validate and fetch in one call:

```bash
bash {base_dir}/../../scripts/fetch_proxies.sh --url "https://example.com" host1:port1 host2:port2
```

Prints the response body fetched through the first working proxy.
Empty stdout means all proxies are dead or the fetch failed.

To just find a working proxy without fetching:

```bash
bash {base_dir}/../../scripts/fetch_proxies.sh host1:port1 host2:port2
```

Prints `host:port` of the first working proxy.

**Options:**
- `--all` — print all working proxies (without `--url`)
- `--timeout S` — validation timeout per proxy (default 29s)
- `--url-timeout S` — fetch timeout for `--url` (default 60s)

**Exit code is always 0** — check stdout for results.

## Retry strategy

If validation returns empty stdout (all dead) or times out:

1. Call `--list` again (the API returns different random servers each time).
2. Extract new host:port pairs yourself (you are an LLM, read the JSON).
3. Call the script again with the new candidates.
4. After 3 failed rounds, inform the user that no working proxies are
   available for this country right now. Suggest trying a different country.

## Countries with free servers

The API typically provides free servers for: **DE, LT, LV, NL, SG, UK, US**.
All other countries usually require premium tier.

## Required permissions (Claude Code)

For silent operation in Claude Code, the user's `settings.json` should include:

```json
"permissions": {
  "allow": [
    "Bash(bash */fetch_proxies.sh *)"
  ]
}
```

Without these, Claude Code will prompt on each call. The user can select
"Yes, and don't ask again" to auto-approve for the session.

## Error handling

- **Connection timeout on fetch** — retry once, then report.
- **No proxies for country** — suggest nearby country or re-fetch.
- **All proxies dead** — re-fetch (random rotation) and try again.
