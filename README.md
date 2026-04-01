# browsec-skills

A collection of [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skills for geo-aware agent tasks using [Browsec](https://browsec.com) VPN proxies.

## Available Skills

### browsec-proxy

Fetch and validate HTTPS proxies from the Browsec API so agents can route requests through specific countries.

**Install:**

```
/plugin marketplace add mzsrn/skills
/plugin install browsec-proxy@browsec-skills
```

**When to use:**

- **Geo-blocked content** — access websites, APIs, and services restricted to specific countries
- **Subscription & SaaS pricing** — compare prices across regions (often 2-5x cheaper in developing countries)
- **Travel & booking** — find cheaper flights, hotels, and car rentals by searching from different countries
- **Regional availability** — check if a product or service is available in a specific market
- **App store prices** — compare app and in-app purchase pricing across regions
- **Ad & SEO verification** — see what ads, search results, and landing pages look like in a target market
- **E-commerce price arbitrage** — find the cheapest region for software licenses, electronics, and digital goods
- **Localization QA** — verify geo-targeting, language redirects, and legal disclaimers work correctly per region
- **Market research** — scrape localized catalogs, competitor pricing, and regional promotions

## License

MIT
