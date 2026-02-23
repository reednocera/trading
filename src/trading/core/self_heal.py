from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RepairPolicy:
    max_retries: int = 2


def should_retry(attempt: int, policy: RepairPolicy) -> bool:
    return attempt < policy.max_retries
