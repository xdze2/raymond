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
import time
from datetime import date
from pathlib import Path

from flask import Flask, abort, jsonify, request, send_from_directory

from build_index import REPO_ROOT, resolve_wiki, write_index
from explore import ExploreError, explore_entry
from llm import DEFAULT_MODEL, render_prompt, run_llm

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
        print(f"[reindex] {n} entries", flush=True)
        return jsonify({"ok": True, "entries": n})

    @app.post("/api/generate")
    def generate():
        body = request.get_json(silent=True) or {}
        axes = body.get("axes") or {}
        n = int(body.get("n", 5))
        existing = body.get("existing") or []
        if not isinstance(axes, dict):
            abort(400, description="axes must be an object")
        if not isinstance(existing, list):
            abort(400, description="existing must be a list")

        config = _load_wiki_config(wiki_dir)

        # Normalise axes: each value can be a string or list of strings.
        # Empty / missing axes render as "any".
        gen_axes = config.get("gen_axes", [])
        rendered_axes: dict[str, str] = {}
        single_axes: dict[str, str] = {}
        for axis_id in gen_axes:
            v = axes.get(axis_id)
            if v is None or v == "" or v == []:
                rendered_axes[axis_id] = "any"
            elif isinstance(v, list):
                rendered_axes[axis_id] = ", ".join(str(x) for x in v) or "any"
                if len(v) == 1:
                    single_axes[axis_id] = str(v[0])
            else:
                rendered_axes[axis_id] = str(v)
                single_axes[axis_id] = str(v)

        template_path = prompts_dir / "make_list.txt"
        if not template_path.is_file():
            abort(500, description="make_list.txt prompt missing")
        template = template_path.read_text()

        existing_block = (
            "\n".join(f"- {t}" for t in existing if isinstance(t, str))
            or "(none yet)"
        )

        prompt = render_prompt(
            template,
            n=str(n),
            existing=existing_block,
            **rendered_axes,
        )

        axes_summary = ", ".join(f"{k}={v}" for k, v in rendered_axes.items())
        model = (config.get("models") or {}).get("make_list", DEFAULT_MODEL)
        print(
            f"[generate] n={n} existing={len(existing)} axes: {axes_summary}",
            flush=True,
        )
        print(f"[generate] prompt={len(prompt)} chars → {model}…", flush=True)

        t0 = time.monotonic()
        try:
            raw = run_llm(prompt, model=model)
        except Exception as e:
            print(f"[generate] LLM call failed after {time.monotonic() - t0:.1f}s: {e}", flush=True)
            abort(502, description=f"LLM call failed: {e}")
        dt = time.monotonic() - t0
        print(f"[generate] {model} returned {len(raw)} chars in {dt:.1f}s", flush=True)

        candidates = _parse_jsonl(raw)
        print(f"[generate] parsed {len(candidates)} candidate entries", flush=True)

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
            entry.setdefault("axes", dict(single_axes))
            entry["created"] = {"at": _today(), "by": "llm"}
            _write_entry(wiki_dir, entry)
            written.append(slug)

        print(
            f"[generate] wrote {len(written)} ({', '.join(written) or '—'}), "
            f"skipped {len(skipped)}",
            flush=True,
        )

        write_index(wiki_dir)
        return jsonify({"ok": True, "written": written, "skipped": skipped})

    @app.post("/api/entries/<slug>/explore")
    def explore(slug: str):
        # Validate slug + existence here so the route still returns 400/404
        # (ExploreError otherwise becomes 502 below).
        _read_entry(wiki_dir, slug)

        def log(msg: str) -> None:
            print(msg, flush=True)

        fetch = request.args.get("fetch", "1").lower() not in ("0", "false", "no")
        query = request.args.get("query") or None

        try:
            entry = explore_entry(
                wiki_dir, slug, fetch=fetch, query=query, log=log,
            )
        except ExploreError as e:
            log(f"[explore] failed ({e.kind}): {e}")
            status = {"config": 500}.get(e.kind, 502)
            abort(status, description=str(e))

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

        changed = sorted(k for k in body if k != "slug" and existing.get(k) != body.get(k))
        print(f"[save] slug={slug} changed={changed or '—'}", flush=True)

        _write_entry(wiki_dir, merged)
        write_index(wiki_dir)
        return jsonify(merged)

    def _nocache(resp):
        # Dev server: backend can rewrite index.jsonl / catalogue files at any
        # time; stale browser caches were causing filter state to desync.
        resp.headers["Cache-Control"] = "no-store"
        return resp

    @app.get("/")
    def index():
        return _nocache(send_from_directory(FRONTEND_DIR, "index.html"))

    @app.get("/<path:filename>")
    def serve(filename: str):
        # block path traversal
        if ".." in filename.split("/"):
            abort(404)

        first = filename.split("/", 1)[0]

        if filename in WIKI_PASSTHROUGH:
            return _nocache(send_from_directory(wiki_dir, filename))

        if first in WIKI_DIR_PASSTHROUGH:
            return _nocache(send_from_directory(wiki_dir, filename))

        return _nocache(send_from_directory(FRONTEND_DIR, filename))

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
