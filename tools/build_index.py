"""Build a wiki's index.jsonl from its catalogue/*.json files.

Usage:
    python tools/build_index.py <wiki>

Resolves <wiki> relative to the repo's wikis/ directory.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
WIKIS_DIR = REPO_ROOT / "wikis"


def build_index(wiki_dir: Path) -> list[dict]:
    catalogue = wiki_dir / "catalogue"
    if not catalogue.is_dir():
        raise FileNotFoundError(f"no catalogue/ in {wiki_dir}")

    entries: list[dict] = []
    for path in sorted(catalogue.glob("*.json")):
        with path.open() as f:
            entry = json.load(f)
        entry.setdefault("status", "generated")
        entries.append(entry)
    return entries


def write_index(wiki_dir: Path) -> Path:
    entries = build_index(wiki_dir)
    out = wiki_dir / "index.jsonl"
    with out.open("w") as f:
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return out


def resolve_wiki(name: str) -> Path:
    p = Path(name)
    if p.is_absolute() and p.is_dir():
        return p
    candidate = WIKIS_DIR / name
    if not candidate.is_dir():
        raise SystemExit(f"wiki not found: {candidate}")
    return candidate


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wiki", help="wiki name (folder under wikis/) or absolute path")
    args = parser.parse_args(argv)

    wiki_dir = resolve_wiki(args.wiki)
    out = write_index(wiki_dir)
    n = sum(1 for _ in out.open())
    print(f"wrote {out.relative_to(REPO_ROOT)} ({n} entries)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
