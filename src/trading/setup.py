from __future__ import annotations

import importlib
import importlib.util
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Callable
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class _SimpleConsole:
    def print(self, msg: str) -> None:
        print(msg)

    def input(self, prompt: str) -> str:
        return input(prompt)


def _build_console():
    if importlib.util.find_spec("rich") is not None:
        rich_console = importlib.import_module("rich.console")
        return rich_console.Console()
    return _SimpleConsole()


console = _build_console()


@dataclass(frozen=True)
class KeySpec:
    env_name: str
    prompt: str
    validator_name: str
    required: bool = True


class SetupWizard:
    def __init__(self, env_path: str | Path = ".env") -> None:
        self.env_path = Path(env_path)
        self.key_specs = [
            KeySpec("ANTHROPIC_API_KEY", "Anthropic API key", "validate_anthropic"),
            KeySpec("FINNHUB_API_KEY", "Finnhub API key", "validate_finnhub"),
            KeySpec("FMP_API_KEY", "Financial Modeling Prep API key", "validate_fmp"),
            KeySpec("TWELVE_DATA_API_KEY", "Twelve Data API key", "validate_twelve_data"),
            KeySpec("ALPHA_VANTAGE_API_KEY", "Alpha Vantage API key", "validate_alpha_vantage"),
            KeySpec("FRED_API_KEY", "FRED API key", "validate_fred"),
            KeySpec("GDELT_API_KEY", "GDELT key/token (optional, use 'NONE' if not required)", "validate_gdelt", required=False),
        ]

    def has_all_required(self) -> bool:
        required = [k.env_name for k in self.key_specs if k.required]
        return all(bool(os.getenv(name)) for name in required)

    def clear_existing(self) -> None:
        for spec in self.key_specs:
            os.environ.pop(spec.env_name, None)
        if self.env_path.exists():
            self.env_path.unlink()

    def run(self) -> None:
        validated: dict[str, str] = {}
        for spec in self.key_specs:
            validator: Callable[[str], bool] = getattr(self, spec.validator_name)
            while True:
                existing = os.getenv(spec.env_name)
                if existing:
                    candidate = existing.strip()
                elif spec.required:
                    candidate = console.input(f"{spec.prompt}: ").strip()
                else:
                    # Optional providers are truly optional; skip prompt unless preset.
                    break

                if not candidate:
                    if spec.required:
                        console.print(f"{spec.env_name} is required.")
                        continue
                    break

                ok = validator(candidate)
                if ok:
                    validated[spec.env_name] = candidate
                    os.environ[spec.env_name] = candidate
                    console.print(f"OK {spec.env_name}")
                    break

                if spec.required:
                    console.print(f"Canary failed for {spec.env_name}. Please re-enter.")
                    if existing:
                        break
                else:
                    console.print(f"Skipping optional {spec.env_name}; validation failed.")
                    break

        self._write_env(validated)

    def _write_env(self, validated: dict[str, str]) -> None:
        if not validated:
            return
        lines = [f"{k}={v}" for k, v in validated.items()]
        self.env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def validate_anthropic(self, key: str) -> bool:
        if not key:
            return False
        payload = json.dumps(
            {
                "model": "claude-4-5-haiku-latest",
                "max_tokens": 1,
                "messages": [{"role": "user", "content": "ping"}],
            }
        ).encode("utf-8")
        req = Request(
            "https://api.anthropic.com/v1/messages",
            data=payload,
            headers={
                "x-api-key": key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            method="POST",
        )
        return self._request_status_ok(req)

    def validate_finnhub(self, key: str) -> bool:
        return self._status_ok("https://finnhub.io/api/v1/quote", {"symbol": "AAPL", "token": key})

    def validate_fmp(self, key: str) -> bool:
        return self._status_ok("https://financialmodelingprep.com/api/v3/quote/AAPL", {"apikey": key})

    def validate_twelve_data(self, key: str) -> bool:
        return self._status_ok(
            "https://api.twelvedata.com/time_series",
            {"symbol": "AAPL", "interval": "1min", "apikey": key},
        )

    def validate_alpha_vantage(self, key: str) -> bool:
        return self._status_ok(
            "https://www.alphavantage.co/query",
            {"function": "GLOBAL_QUOTE", "symbol": "AAPL", "apikey": key},
        )

    def validate_fred(self, key: str) -> bool:
        return self._status_ok(
            "https://api.stlouisfed.org/fred/series",
            {"series_id": "GNP", "api_key": key, "file_type": "json"},
        )

    def validate_gdelt(self, key: str) -> bool:
        _ = key
        return self._status_ok(
            "https://api.gdeltproject.org/api/v2/doc/doc",
            {"query": "AAPL", "mode": "ArtList", "format": "json", "maxrecords": 1},
        )

    @staticmethod
    def _request_status_ok(request: Request) -> bool:
        try:
            with urlopen(request, timeout=10) as response:
                return response.status == 200
        except URLError:
            return False

    @classmethod
    def _status_ok(cls, url: str, params: dict[str, str]) -> bool:
        query = urlencode(params)
        req = Request(f"{url}?{query}", method="GET")
        return cls._request_status_ok(req)


def maybe_run_setup_wizard() -> None:
    wizard = SetupWizard()
    if wizard.has_all_required():
        return
    console.print("Configuration missing; launching setup wizard.")
    wizard.run()


def reset_setup() -> None:
    wizard = SetupWizard()
    console.print("Resetting setup: clearing stored environment keys and restarting install wizard.")
    wizard.clear_existing()
    wizard.run()
