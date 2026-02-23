from __future__ import annotations

import importlib
import importlib.util
import os
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from trading.config import load_config
from trading.data.quota import QuotaManager


class _FallbackMCP:
    def __init__(self, _name: str) -> None:
        self.tools = []

    def tool(self):
        def decorator(fn):
            self.tools.append(fn)
            return fn

        return decorator

    def run(self) -> None:
        return


def _build_mcp():
    if importlib.util.find_spec("fastmcp") is None:
        return _FallbackMCP("MarketOracle")
    fastmcp = importlib.import_module("fastmcp")
    return fastmcp.FastMCP("MarketOracle")


def _quota_limits_from_config() -> dict[str, int]:
    cfg = load_config()
    raw = cfg.mcp.get("quotas", {})
    return {
        "YAHOO": int(raw.get("yahoo", 100000)),
        "STOOQ": int(raw.get("stooq", 100000)),
        "TWELVE_DATA": int(raw.get("twelvedata", 800)),
        "FINNHUB": int(raw.get("finnhub", 50000)),
        "FMP": int(raw.get("fmp", 250)),
        "ALPHA_VANTAGE": int(raw.get("alphavantage", 25)),
        "FRED": int(raw.get("fred", 10000)),
        "GDELT": int(raw.get("gdelt", 1000)),
        "SEC_EDGAR": int(raw.get("sec_edgar", 10000)),
    }


mcp = _build_mcp()
quota = QuotaManager(limits=_quota_limits_from_config())


def _quota_error(provider: str) -> str:
    return f"ERROR: {provider} QUOTA_EXCEEDED"


def _get(url: str, params: dict[str, Any]) -> str:
    query = urlencode(params)
    req = Request(f"{url}?{query}", method="GET")
    with urlopen(req, timeout=10) as response:
        return response.read().decode("utf-8")


@mcp.tool()
def get_price(symbol: str) -> str:
    if quota.check_and_consume("YAHOO"):
        return _get("https://query1.finance.yahoo.com/v7/finance/quote", {"symbols": symbol})
    if quota.check_and_consume("STOOQ"):
        return _get("https://stooq.com/q/l/", {"s": symbol.lower(), "f": "sd2t2ohlcv", "e": "json"})
    if quota.check_and_consume("TWELVE_DATA"):
        return _get("https://api.twelvedata.com/quote", {"symbol": symbol, "apikey": os.getenv("TWELVE_DATA_API_KEY", "")})
    if quota.check_and_consume("FINNHUB"):
        return _get("https://finnhub.io/api/v1/quote", {"symbol": symbol, "token": os.getenv("FINNHUB_API_KEY", "")})
    return _quota_error("FINNHUB")


@mcp.tool()
def finnhub_quote(symbol: str) -> str:
    if not quota.check_and_consume("FINNHUB"):
        return _quota_error("FINNHUB")
    return _get("https://finnhub.io/api/v1/quote", {"symbol": symbol, "token": os.getenv("FINNHUB_API_KEY", "")})


@mcp.tool()
def fmp_quote(symbol: str) -> str:
    if not quota.check_and_consume("FMP"):
        return _quota_error("FMP")
    return _get(f"https://financialmodelingprep.com/api/v3/quote/{symbol}", {"apikey": os.getenv("FMP_API_KEY", "")})


@mcp.tool()
def twelve_data_series(symbol: str, interval: str = "1min") -> str:
    if not quota.check_and_consume("TWELVE_DATA"):
        return _quota_error("TWELVE_DATA")
    return _get("https://api.twelvedata.com/time_series", {"symbol": symbol, "interval": interval, "apikey": os.getenv("TWELVE_DATA_API_KEY", "")})


@mcp.tool()
def alpha_vantage_global_quote(symbol: str) -> str:
    if not quota.check_and_consume("ALPHA_VANTAGE"):
        return _quota_error("ALPHA_VANTAGE")
    return _get("https://www.alphavantage.co/query", {"function": "GLOBAL_QUOTE", "symbol": symbol, "apikey": os.getenv("ALPHA_VANTAGE_API_KEY", "")})


@mcp.tool()
def fred_series(series_id: str = "GNP") -> str:
    if not quota.check_and_consume("FRED"):
        return _quota_error("FRED")
    return _get("https://api.stlouisfed.org/fred/series", {"series_id": series_id, "api_key": os.getenv("FRED_API_KEY", ""), "file_type": "json"})


@mcp.tool()
def gdelt_search(query: str = "AAPL") -> str:
    if not quota.check_and_consume("GDELT"):
        return _quota_error("GDELT")
    return _get("https://api.gdeltproject.org/api/v2/doc/doc", {"query": query, "mode": "ArtList", "format": "json", "maxrecords": 10})


@mcp.tool()
def sec_edgar_submissions(cik: str) -> str:
    if not quota.check_and_consume("SEC_EDGAR"):
        return _quota_error("SEC_EDGAR")
    padded_cik = str(cik).zfill(10)
    return _get(f"https://data.sec.gov/submissions/CIK{padded_cik}.json", {})


def run() -> None:
    mcp.run()
