from __future__ import annotations

import json
import re
from dataclasses import dataclass
from xml.sax.saxutils import escape

from trading.config import AppConfig

EXECUTION_ORDERS_RE = re.compile(
    r"<execution_orders>\s*(\[.*?\])\s*</execution_orders>",
    re.S,
)


@dataclass(frozen=True)
class StrategyAsset:
    symbol: str
    status: str
    features: dict


@dataclass
class AnthropicRouter:
    config: AppConfig

    def cached_system_block(self, system_rules: str) -> dict:
        return {
            "type": "text",
            "text": f"<system_rules>\n{escape(system_rules)}\n</system_rules>",
            "cache_control": {"type": "ephemeral"},
        }

    def extract_execution_orders(self, model_text: str) -> list[dict]:
        match = EXECUTION_ORDERS_RE.search(model_text)
        if not match:
            raise ValueError("Missing <execution_orders> JSON array block")
        parsed = json.loads(match.group(1))
        if not isinstance(parsed, list):
            raise ValueError("<execution_orders> must contain a JSON array")
        return parsed

    def compile_strategy_director_prompt(
        self,
        *,
        global_portfolio_state: dict,
        assets: list[StrategyAsset],
    ) -> str:
        market_assets = []
        for asset in assets:
            market_assets.append(
                "\n".join(
                    [
                        "  <asset>",
                        f"    <symbol>{escape(asset.symbol)}</symbol>",
                        f"    <status>{escape(asset.status)}</status>",
                        "    <features>",
                        escape(json.dumps(asset.features, separators=(",", ":"))),
                        "    </features>",
                        "  </asset>",
                    ]
                )
            )

        return "\n\n".join(
            [
                "<global_portfolio_state>\n"
                f"{escape(json.dumps(global_portfolio_state, separators=(',', ':')))}\n"
                "</global_portfolio_state>",
                "<market_data>\n" + "\n".join(market_assets) + "\n</market_data>",
                "<instructions>\n"
                "Evaluate the <market_data> against the <system_rules> and <global_portfolio_state>.\n"
                "You must debate your correlation checks, portfolio improvement tests, and edge rankings inside <thinking> tags.\n"
                "If trades are justified, output ONLY a valid JSON array of order objects inside <execution_orders> tags. If no trades are justified, output [].\n"
                "</instructions>",
            ]
        )

    def build_strategy_payload(
        self,
        *,
        system_rules: str,
        global_portfolio_state: dict,
        assets: list[StrategyAsset],
        tools: list[str],
    ) -> dict:
        return {
            "model": self.config.models.get("strategy_director", "claude-4-6-opus-latest"),
            "thinking": {"type": self.config.raw.get("anthropic", {}).get("thinking", "adaptive")},
            "system": [self.cached_system_block(system_rules)],
            "tools": [{"name": name} for name in tools],
            "messages": [
                {
                    "role": "user",
                    "content": self.compile_strategy_director_prompt(
                        global_portfolio_state=global_portfolio_state,
                        assets=assets,
                    ),
                }
            ],
        }
