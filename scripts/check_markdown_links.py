#!/usr/bin/env python3
"""Fail when a repository-local Markdown link points at a missing path."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")


def local_target(raw: str) -> str | None:
    target = raw.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    else:
        # Optional Markdown title: path "title".
        target = target.split(maxsplit=1)[0]
    if not target or target.startswith("#"):
        return None
    parsed = urlsplit(target)
    if parsed.scheme or parsed.netloc:
        return None
    return unquote(parsed.path) or None


def main() -> int:
    broken: list[str] = []
    for markdown in sorted(ROOT.rglob("*.md")):
        if ".git" in markdown.parts:
            continue
        text = markdown.read_text(encoding="utf-8")
        for match in LINK_RE.finditer(text):
            target = local_target(match.group(1))
            if target is None:
                continue
            resolved = (markdown.parent / target).resolve()
            try:
                resolved.relative_to(ROOT)
            except ValueError:
                broken.append(f"{markdown.relative_to(ROOT)}: link escapes repository: {target}")
                continue
            if not resolved.exists():
                broken.append(f"{markdown.relative_to(ROOT)}: missing {target}")

    if broken:
        print("Broken local Markdown links:", file=sys.stderr)
        for item in broken:
            print(f"- {item}", file=sys.stderr)
        return 1
    print("All repository-local Markdown links resolve.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
