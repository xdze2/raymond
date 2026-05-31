"""Dev server: serve the shared frontend layered over one wiki's data.

Usage:
    python tools/dev_server.py <wiki> [--port 8765]

Same-origin layout from the browser's point of view:
    /                                  → frontend/index.html
    /style.css                         → frontend/style.css
    /wiki.json                         → wikis/<wiki>/wiki.json
    /axis.json                         → wikis/<wiki>/axis.json
    /index.jsonl                       → wikis/<wiki>/index.jsonl  (rebuilt at startup)
    /media/...                         → wikis/<wiki>/media/...
    /pages/...                         → wikis/<wiki>/pages/...
    /api/health                        → JSON
    /api/reindex                       → POST, rebuild index.jsonl
    /api/generate                      → POST {axes, n} → new generated entries
    /api/entries/<slug>/explore        → POST, promote to explored via LLM
    /api/entries/<slug>                → PUT, save manual edits
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

from flask import Flask, abort, jsonify, request, send_from_directory

from build_index import REPO_ROOT, resolve_wiki, write_index
from llm import render_prompt, run_claude

FRONTEND_DIR = REPO_ROOT / "frontend"
WIKI_PASSTHROUGH = {"wiki.json", "axis.json", "index.jsonl"}
WIKI_DIR_PASSTHROUGH = {"media", "pages"}

SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def _today() -> str:
    return date.today().isoformat()


def _load_wiki_config(wiki_dir: Path) -> dict:
    with (wiki_dir / "wiki.json").open() as f:
        return json.load(f)


def _read_entry(wiki_dir: Path, slug: str) -> dict:
    if not SLUG_RE.match(slug):
        abort(400, description="invalid slug")
    path = wiki_dir / "catalogue" / f"{slug}.json"
    if not path.is_file():
        abort(404, description="entry not found")
    with path.open() as f:
        return json.load(f)


def _write_entry(wiki_dir: Path, entry: dict) -> Path:
    slug = entry["slug"]
    if not SLUG_RE.match(slug):
        raise ValueError(f"invalid slug: {slug!r}")
    path = wiki_dir / "catalogue" / f"{slug}.json"
    with path.open("w") as f:
        json.dump(entry, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return path


def _parse_jsonl(text: str) -> list[dict]:
    out: list[dict] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        # tolerate ```json fences
        if line.startswith("```"):
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def _parse_json_blob(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        # strip leading fence line and trailing ```
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)
    return json.loads(text)


def make_app(wiki_dir: Path) -> Flask:
    app = Flask(__name__)
    wiki_name = wiki_dir.name
    prompts_dir = wiki_dir / "prompts"
    write_index(wiki_dir)

    @app.get("/api/health")
    def health():
        return jsonify({"mode": "dev", "wiki": wiki_name})

    @app.post("/api/reindex")
    def reindex():
        out = write_index(wiki_dir)
        n = sum(1 for _ in out.open())
        return jsonify({"ok": True, "entries": n})

    @app.post("/api/generate")
    def generate():
        body = request.get_json(silent=True) or {}
        axes = body.get("axes") or {}
        n = int(body.get("n", 5))
        if not isinstance(axes, dict) or not axes:
            abort(400, description="missing axes")

        config = _load_wiki_config(wiki_dir)
        for axis_id in config.get("gen_axes", []):
            if axis_id not in axes:
                abort(400, description=f"missing axis: {axis_id}")

        template_path = prompts_dir / "make_list.txt"
        if not template_path.is_file():
            abort(500, description="make_list.txt prompt missing")
        template = template_path.read_text()

        prompt = render_prompt(template, n=str(n), **{k: str(v) for k, v in axes.items()})

        try:
            raw = run_claude(prompt)
        except Exception as e:
            abort(502, description=f"LLM call failed: {e}")

        candidates = _parse_jsonl(raw)
        written: list[str] = []
        skipped: list[dict] = []
        for entry in candidates:
            slug = entry.get("slug")
            if not slug or not SLUG_RE.match(slug):
                skipped.append({"reason": "invalid slug", "entry": entry})
                continue
            if (wiki_dir / "catalogue" / f"{slug}.json").exists():
                skipped.append({"reason": "exists", "slug": slug})
                continue
            entry.setdefault("status", "generated")
            entry.setdefault("axes", axes)
            entry["created"] = {"at": _today(), "by": "llm"}
            _write_entry(wiki_dir, entry)
            written.append(slug)

        write_index(wiki_dir)
        return jsonify({"ok": True, "written": written, "skipped": skipped})

    @app.post("/api/entries/<slug>/explore")
    def explore(slug: str):
        entry = _read_entry(wiki_dir, slug)

        template_path = prompts_dir / "make_page.txt"
        if not template_path.is_file():
            abort(500, description="make_page.txt prompt missing")
        template = template_path.read_text()
        prompt = render_prompt(template, seed=json.dumps(entry, indent=2, ensure_ascii=False))

        try:
            raw = run_claude(prompt)
        except Exception as e:
            abort(502, description=f"LLM call failed: {e}")

        try:
            payload = _parse_json_blob(raw)
        except json.JSONDecodeError as e:
            abort(502, description=f"LLM returned non-JSON: {e}")

        if "facts" in payload:
            entry["facts"] = payload["facts"]
        if "links" in payload:
            entry["links"] = payload["links"]
        if "image" in payload:
            entry["image"] = payload["image"]
        entry["status"] = "explored"
        entry["updated"] = {"at": _today(), "by": "llm"}

        _write_entry(wiki_dir, entry)
        write_index(wiki_dir)
        return jsonify(entry)

    @app.put("/api/entries/<slug>")
    def save(slug: str):
        existing = _read_entry(wiki_dir, slug)
        body = request.get_json(silent=True)
        if not isinstance(body, dict):
            abort(400, description="expected JSON object")
        if body.get("slug", slug) != slug:
            abort(400, description="slug in body does not match URL")

        merged = {**existing, **body, "slug": slug}
        merged["updated"] = {"at": _today(), "by": "user"}

        _write_entry(wiki_dir, merged)
        write_index(wiki_dir)
        return jsonify(merged)

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
    app = make_app(wiki_dir)
    print(f"refreshed {(wiki_dir / 'index.jsonl').relative_to(REPO_ROOT)}")
    print(f"serving wiki '{wiki_dir.name}' at http://{args.host}:{args.port}/")
    app.run(host=args.host, port=args.port, debug=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
