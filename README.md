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

## Notes
This remains scaffold-first and intentionally defers full production integrations.


## Setup notes
- Reddit credentials are optional and are no longer required to complete setup or run core flows.
