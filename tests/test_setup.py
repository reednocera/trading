from trading.setup import SetupWizard


def test_write_env_only_when_validated(tmp_path):
    wizard = SetupWizard(env_path=tmp_path / ".env")
    wizard._write_env({"A": "1", "B": "2"})
    assert (tmp_path / ".env").read_text().strip().splitlines() == ["A=1", "B=2"]
