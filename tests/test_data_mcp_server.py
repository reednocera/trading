from trading.data import mcp_server


def test_quota_exceeded_error_format():
    mcp_server.quota.usage["FMP"] = mcp_server.quota.limits["FMP"]
    out = mcp_server.fmp_quote("AAPL")
    assert out == "ERROR: FMP QUOTA_EXCEEDED"


def test_config_driven_quota_loaded_for_twelve_data():
    assert "TWELVE_DATA" in mcp_server.quota.limits
