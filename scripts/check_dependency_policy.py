#!/usr/bin/env python3
"""Dependency policy guard for pyproject.toml."""

from __future__ import annotations

import re
import sys
try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib
from pathlib import Path
from typing import Any

POLICY_MESSAGE = "Reddit integrations are intentionally removed from this project."
BLOCKED_PACKAGES = {
    "praw",
    "asyncpraw",
    "prawcore",
    "reddit",
    "reddit-sdk",
}


def normalize_name(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name.strip().lower())


def extract_requirement_name(requirement: str) -> str:
    match = re.match(r"\s*([A-Za-z0-9_.-]+)", requirement)
    return normalize_name(match.group(1)) if match else ""


def contains_blocked_dependency_name(name: str) -> bool:
    normalized = normalize_name(name)
    return normalized in BLOCKED_PACKAGES


def find_blocked_dependency_entries(pyproject: dict[str, Any]) -> list[str]:
    blocked: list[str] = []

    dependencies = pyproject.get("project", {}).get("dependencies", [])
    for entry in dependencies:
        if isinstance(entry, str) and contains_blocked_dependency_name(extract_requirement_name(entry)):
            blocked.append(f"project.dependencies -> {entry}")

    optional_deps = pyproject.get("project", {}).get("optional-dependencies", {})
    for group, entries in optional_deps.items():
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if isinstance(entry, str) and contains_blocked_dependency_name(extract_requirement_name(entry)):
                blocked.append(f"project.optional-dependencies.{group} -> {entry}")

    def visit(obj: Any, path: str = "") -> None:
        if isinstance(obj, dict):
            for key, value in obj.items():
                key_str = str(key)
                current_path = f"{path}.{key_str}" if path else key_str
                if contains_blocked_dependency_name(key_str):
                    blocked.append(f"{current_path} (dependency key)")
                visit(value, current_path)
        elif isinstance(obj, list):
            for idx, item in enumerate(obj):
                visit(item, f"{path}[{idx}]")

    visit(pyproject)
    return sorted(set(blocked))


def main() -> int:
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        print("pyproject.toml not found.", file=sys.stderr)
        return 2

    with pyproject_path.open("rb") as f:
        pyproject = tomllib.load(f)

    blocked_entries = find_blocked_dependency_entries(pyproject)
    if blocked_entries:
        print(POLICY_MESSAGE, file=sys.stderr)
        print("Blocked dependency entries found:", file=sys.stderr)
        for entry in blocked_entries:
            print(f"- {entry}", file=sys.stderr)
        return 1

    print("Dependency policy check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
