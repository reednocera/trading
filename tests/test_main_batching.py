from trading.main import run_decision


def test_run_decision_builds_30_asset_batch_from_config():
    payload = run_decision()
    msg = payload["messages"][0]["content"]
    assert msg.count("<asset>") == 30
    assert "<status>holding</status>" in msg
    assert "<status>watchlist</status>" in msg
