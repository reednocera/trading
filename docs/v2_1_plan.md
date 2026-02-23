# V2.1 Implementation Plan

## Confirmed decisions
- Anthropic SDK range `>=0.80.0`.
- Composio local API key + direct SDK.
- SQLAlchemy async + asyncpg for Postgres.
- Single multiplexed MCP server.
- XML/JSON auto-repair retry max 2 before `no_trade`.
- 16:30 batch with backoff retries until 20:00 ET.
- Python computes deterministic risk metrics; Opus performs final enforcement decision.
- Earnings tools injected for configurable T-1 to T+2 window.

## Additional delivered scaffolding
- Setup Wizard (`src/trading/setup.py`) with interactive key prompts and canary validation endpoints.
- Unified data layer (`src/trading/data/mcp_server.py`) using one `FastMCP("MarketOracle")` server and provider tools.
- Quota wrapping at tool boundary with standard `ERROR: [PROVIDER] QUOTA_EXCEEDED` output.
- Async state models (`src/trading/state/models.py`) for global portfolio state, positions (30-asset view), and attribution.
- Strategy Director refinement (`src/trading/agents/director.py`) enforcing full 30-asset batch and cross-correlation thinking requirement.

## Prompt compiler constraints
- Strategy Director prompt is batched into a single Opus call for 30 assets.
- User message hierarchy is strict:
  - `<global_portfolio_state>`
  - `<market_data>` with repeated `<asset>` blocks containing `<symbol>`, `<status>`, and `<features>`
  - `<instructions>`
- `<execution_orders>` parser accepts JSON array only.

## Unsupported data source policy

Reddit is intentionally unsupported in this codebase.

Contributors should not add Reddit or PRAW dependencies, API keys, MCP tools, quotas, or documentation references in `src`, `tests`, `config`, `pyproject.toml`, or `README.md`.

CI enforces this with a guard step that fails when those references are present.
