import os

from trading.setup import SetupWizard


def test_write_env_only_when_validated(tmp_path):
    wizard = SetupWizard(env_path=tmp_path / ".env")
    wizard._write_env({"A": "1", "B": "2"})
    assert (tmp_path / ".env").read_text().strip().splitlines() == ["A=1", "B=2"]


def test_optional_provider_not_required_for_setup(monkeypatch):
    for key in [
        "ANTHROPIC_API_KEY",
        "FINNHUB_API_KEY",
        "FMP_API_KEY",
        "TWELVE_DATA_API_KEY",
        "ALPHA_VANTAGE_API_KEY",
        "FRED_API_KEY",
    ]:
        monkeypatch.setenv(key, "x")

    monkeypatch.delenv("GDELT_API_KEY", raising=False)

    wizard = SetupWizard()
    assert wizard.has_all_required()


def test_optional_provider_values_can_be_written(tmp_path):
    wizard = SetupWizard(env_path=tmp_path / ".env")
    wizard._write_env({"GDELT_API_KEY": "none"})
    content = (tmp_path / ".env").read_text()
    assert "GDELT_API_KEY=none" in content


def test_clear_existing_removes_env_and_file(monkeypatch, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("ANTHROPIC_API_KEY=x\n", encoding="utf-8")

    monkeypatch.setenv("ANTHROPIC_API_KEY", "x")
    monkeypatch.setenv("FINNHUB_API_KEY", "x")

    wizard = SetupWizard(env_path=env_file)
    wizard.clear_existing()

    assert "ANTHROPIC_API_KEY" not in os.environ
    assert "FINNHUB_API_KEY" not in os.environ
    assert not env_file.exists()


def test_optional_providers_do_not_prompt(monkeypatch, tmp_path):
    for key in [
        "ANTHROPIC_API_KEY",
        "FINNHUB_API_KEY",
        "FMP_API_KEY",
        "TWELVE_DATA_API_KEY",
        "ALPHA_VANTAGE_API_KEY",
        "FRED_API_KEY",
    ]:
        monkeypatch.setenv(key, "preset")

    wizard = SetupWizard(env_path=tmp_path / ".env")
    wizard.validate_anthropic = lambda _k: True
    wizard.validate_finnhub = lambda _k: True
    wizard.validate_fmp = lambda _k: True
    wizard.validate_twelve_data = lambda _k: True
    wizard.validate_alpha_vantage = lambda _k: True
    wizard.validate_fred = lambda _k: True

    import trading.setup as setup_module

    def _boom(_prompt: str) -> str:
        raise AssertionError("optional providers should not prompt")

    monkeypatch.setattr(setup_module.console, "input", _boom)

    wizard.run()
