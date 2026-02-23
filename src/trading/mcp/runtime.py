from __future__ import annotations

from dataclasses import dataclass


@dataclass
class MCPRuntime:
    """Scaffold for a single multiplexed local MCP server runtime."""

    started: bool = False

    async def start(self) -> None:
        # TODO: boot a single MCP stdio server process exposing provider tools.
        self.started = True

    async def stop(self) -> None:
        self.started = False
