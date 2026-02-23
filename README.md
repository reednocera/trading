# Adaptive Multi-Agent Paper Portfolio System (V2.1 Scaffold)

Updated scaffold implementing V2.1 overrides with:
- Anthropic routing and strict Strategy Director XML compiler
- 30-asset batched decision payload
- Setup Wizard for key collection + canary validation
- Unified FastMCP multiplexed data server scaffold (`MarketOracle`)
- Async Postgres state model scaffolding for portfolio + attribution

## CLI
- `trading setup` - run setup wizard and write validated `.env`
- `trading plan`
- `trading run-decision`
- `trading run-schedule`

## Supported providers
- Anthropic (LLM routing and decisioning)
- Finnhub
- Financial Modeling Prep (FMP)
- Twelve Data
- Alpha Vantage
- FRED
- GDELT (optional)

Reddit is intentionally **not** integrated as a supported provider in this scaffold.

### Migration note (older branches/configs)
If you are upgrading from an older local configuration, remove any lingering Reddit environment variables from your shell profile, `.env`, and secret managers:
- `REDDIT_CLIENT_ID`
- `REDDIT_CLIENT_SECRET`
- `REDDIT_USER_AGENT`

## Notes
This remains scaffold-first and intentionally defers full production integrations.
