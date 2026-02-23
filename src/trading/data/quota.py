from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class QuotaManager:
    limits: dict[str, int]
    usage: dict[str, int] = field(default_factory=lambda: defaultdict(int))

    def check_and_consume(self, provider: str) -> bool:
        limit = self.limits.get(provider)
        if limit is None:
            return True
        if self.usage[provider] >= limit:
            return False
        self.usage[provider] += 1
        return True
