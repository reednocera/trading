from __future__ import annotations

import json
from dataclasses import dataclass
from xml.sax.saxutils import escape

from trading.config import AppConfig
from trading.infra.anthropic_client import AnthropicRouter, StrategyAsset


@dataclass
class PromptCompiler:
    config: AppConfig

    def compile_xml(self, *, system_rules: str, global_portfolio_state: dict, assets: list[StrategyAsset]) -> str:
        if len(assets) != 30:
            raise ValueError("PromptCompiler requires exactly 30 assets")

        asset_blocks = []
        for asset in assets:
            feature_json = escape(json.dumps(asset.features, separators=(",", ":")))
            asset_blocks.append(
                "\n".join(
                    [
                        "  <asset>",
                        f"    <symbol>{escape(asset.symbol)}</symbol>",
                        f"    <status>{escape(asset.status)}</status>",
                        f"    <features>{feature_json}</features>",
                        "  </asset>",
                    ]
                )
            )

        risk_cfg = self.config.risk
        return "\n".join(
            [
                "<system_rules>",
                escape(system_rules),
                f"min_edge_after_cost_pct={risk_cfg.get('min_edge_after_cost_pct', 0.0)}",
                f"min_win_prob={risk_cfg.get('min_win_prob', 0.0)}",
                "</system_rules>",
                "<global_portfolio_state>",
                escape(json.dumps(global_portfolio_state, separators=(",", ":"))),
                "</global_portfolio_state>",
                "<market_data>",
                *asset_blocks,
                "</market_data>",
                "<instructions>",
                "Analyze the 30-asset basket. Think step-by-step in <thinking> regarding sector risk and sizing.",
                "Output ONLY a JSON array of orders in <execution_orders>.",
                "Before issuing any order, perform a cross-correlation check across all 30 assets.",
                "</instructions>",
            ]
        )


@dataclass
class StrategyDirector:
    router: AnthropicRouter

    def build_batched_prompt(self, *, system_rules: str, global_portfolio_state: dict, assets: list[StrategyAsset]) -> dict:
        compiler = PromptCompiler(config=self.router.config)
        content = compiler.compile_xml(
            system_rules=system_rules,
            global_portfolio_state=global_portfolio_state,
            assets=assets,
        )
        return {
            "model": self.router.config.models.get("strategy_director", "claude-4-6-opus-latest"),
            "thinking": {"type": self.router.config.raw.get("anthropic", {}).get("thinking", "adaptive")},
            "system": [self.router.cached_system_block(system_rules)],
            "messages": [{"role": "user", "content": content}],
            "tools": [],
        }
