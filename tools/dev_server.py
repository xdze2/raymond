"""Dev server: serve the shared frontend layered over one wiki's data.

Usage:
    python tools/dev_server.py <wiki> [--port 8765]

Same-origin layout from the browser's point of view:
    /                 → frontend/index.html
    /style.css        → frontend/style.css
    /wiki.json        → wikis/<wiki>/wiki.json
    /axis.json        → wikis/<wiki>/axis.json
    /index.jsonl      → wikis/<wiki>/index.jsonl  (rebuilt at startup)
    /media/...        → wikis/<wiki>/media/...
    /pages/...        → wikis/<wiki>/pages/...
    /api/health       → JSON
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from flask import Flask, jsonify, send_from_directory, abort

from build_index import write_index, resolve_wiki, REPO_ROOT

FRONTEND_DIR = REPO_ROOT / "frontend"
WIKI_PASSTHROUGH = {"wiki.json", "axis.json", "index.jsonl"}
WIKI_DIR_PASSTHROUGH = {"media", "pages"}


def make_app(wiki_dir: Path) -> Flask:
    app = Flask(__name__)
    wiki_name = wiki_dir.name

    @app.get("/api/health")
    def health():
        return jsonify({"mode": "dev", "wiki": wiki_name})

    @app.get("/")
    def index():
        return send_from_directory(FRONTEND_DIR, "index.html")

    @app.get("/<path:filename>")
    def serve(filename: str):
        # block path traversal
        if ".." in filename.split("/"):
            abort(404)

        first = filename.split("/", 1)[0]

        if filename in WIKI_PASSTHROUGH:
            return send_from_directory(wiki_dir, filename)

        if first in WIKI_DIR_PASSTHROUGH:
            return send_from_directory(wiki_dir, filename)

        return send_from_directory(FRONTEND_DIR, filename)

    return app


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wiki")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--host", default="127.0.0.1")
    args = parser.parse_args(argv)

    wiki_dir = resolve_wiki(args.wiki)
    out = write_index(wiki_dir)
    print(f"refreshed {out.relative_to(REPO_ROOT)}")

    app = make_app(wiki_dir)
    print(f"serving wiki '{wiki_dir.name}' at http://{args.host}:{args.port}/")
    app.run(host=args.host, port=args.port, debug=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
