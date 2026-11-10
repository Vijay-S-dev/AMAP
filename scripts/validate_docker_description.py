#!/usr/bin/env python3
"""
Validate the Docker Hub description files.

Checks that deployment/docker/description/short.md is a single line of at
most 100 characters (Docker Hub's hard limit for the short description)
and that long.md is non-empty. Exits non-zero on any failure, so it can
gate CI.

Usage:
    python scripts/validate_docker_description.py [short.md] [long.md]

Paths default to the repository's staged description files; explicit paths
are accepted for testing.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SHORT = REPO_ROOT / "deployment" / "docker" / "description" / "short.md"
DEFAULT_LONG = REPO_ROOT / "deployment" / "docker" / "description" / "long.md"
MAX_SHORT_CHARS = 100


def _read(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return None


def main(argv: list[str]) -> int:
    short_path = Path(argv[1]) if len(argv) > 1 else DEFAULT_SHORT
    long_path = Path(argv[2]) if len(argv) > 2 else DEFAULT_LONG

    failures: list[str] = []

    short_text = _read(short_path)
    if not short_text:
        failures.append(f"{short_path} is missing or empty")
    else:
        print(f"short description: {short_text}")
        if "\n" in short_text:
            failures.append("short description must be a single line")
        count = len(short_text)
        verdict = "OK" if count <= MAX_SHORT_CHARS else "TOO LONG"
        print(f"character count: {count}/{MAX_SHORT_CHARS} {verdict}")
        if count > MAX_SHORT_CHARS:
            failures.append(
                f"short description is {count} characters (limit {MAX_SHORT_CHARS})"
            )

    long_text = _read(long_path)
    if not long_text:
        failures.append(f"{long_path} is missing or empty")
    else:
        print(f"long description: {len(long_text)} characters, OK")

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print("Docker Hub descriptions: all checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
