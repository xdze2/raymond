"""Build a standalone static bundle for one wiki at dist/<wiki>/.

Usage:
    python tools/export.py <wiki>

The bundle is the shared frontend plus the wiki's data files, with a fresh
index.jsonl. No catalogue/ or prompts/ — those are not needed at runtime.
Serve it with any static HTTP server.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from build_index import write_index, resolve_wiki, REPO_ROOT

FRONTEND_DIR = REPO_ROOT / "frontend"
DIST_DIR = REPO_ROOT / "dist"

WIKI_FILES = ("wiki.json", "axis.json")
WIKI_DIRS = ("media", "pages")


def export(wiki_dir: Path) -> Path:
    out = DIST_DIR / wiki_dir.name
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    for item in FRONTEND_DIR.iterdir():
        dst = out / item.name
        if item.is_dir():
            shutil.copytree(item, dst)
        else:
            shutil.copy2(item, dst)

    for name in WIKI_FILES:
        src = wiki_dir / name
        if src.exists():
            shutil.copy2(src, out / name)

    for name in WIKI_DIRS:
        src = wiki_dir / name
        if src.is_dir() and any(src.iterdir()):
            shutil.copytree(src, out / name)

    write_index(wiki_dir)
    shutil.copy2(wiki_dir / "index.jsonl", out / "index.jsonl")

    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wiki")
    args = parser.parse_args(argv)

    wiki_dir = resolve_wiki(args.wiki)
    out = export(wiki_dir)
    print(f"exported to {out.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
