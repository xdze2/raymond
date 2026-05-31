"""Core: promote a catalogue entry from "generated" to "explored".

Shared by the CLI (`tools/explore_entry.py`) and the Flask route
(`/api/entries/<slug>/explore` in `tools/dev_server.py`). Keep all
prompt rendering, LLM call, parsing, and disk merge in here so both
interfaces stay in sync.
"""

from __future__ import annotations

import json
import re
import subprocess
from datetime import date
from pathlib import Path
from typing import Callable

from llm import DEFAULT_MODEL, render_prompt, run_llm

REPO_ROOT = Path(__file__).resolve().parent.parent
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")

Logger = Callable[[str], None]


def _rel(path: Path) -> str:
    """Format a path relative to REPO_ROOT when possible, else absolute."""
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


class ExploreError(Exception):
    """Recoverable explore failure. `kind` lets callers map to HTTP status."""

    def __init__(self, message: str, *, kind: str = "internal"):
        super().__init__(message)
        self.kind = kind


def parse_json_blob(text: str) -> dict:
    """Tolerate ```json fences and leading/trailing prose around a JSON object."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        return json.loads(text[start : end + 1])


def run_fetch_wiki(
    wiki: str, slug: str, query: str | None, *, log: Logger = print
) -> Path | None:
    """Invoke tools/fetch_wiki.py. Return path to the enrichment file, or None."""
    # fetch_wiki.py is a PEP 723 uv-script; invoke via `uv run --script` so
    # its inline deps (e.g. `requests`) resolve. sys.executable points at the
    # project venv, which doesn't include them.
    cmd = [
        "uv",
        "run",
        "--script",
        str(REPO_ROOT / "tools" / "fetch_wiki.py"),
        "--wiki",
        wiki,
        "--slug",
        slug,
    ]
    if query:
        cmd += ["--query", query]
    log(f"[fetch] $ {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    for line in result.stdout.splitlines():
        log(f"  {line}")
    if result.returncode != 0:
        log(f"[fetch] fetch_wiki.py failed ({result.returncode}): "
            f"{result.stderr.strip()}")
        return None
    enrichment_path = REPO_ROOT / "wikis" / wiki / "enrichments" / f"{slug}.json"
    return enrichment_path if enrichment_path.is_file() else None


def explore_entry(
    wiki_dir: Path,
    slug: str,
    *,
    fetch: bool = True,
    query: str | None = None,
    write: bool = True,
    log: Logger = print,
) -> dict:
    """Promote `slug` to status=explored. Returns the merged entry dict.

    Side effects (when `write=True`): writes catalogue/<slug>.json and (if
    fetch=True) may write enrichments/<slug>.json + media/<slug>/<image>.

    Raises ExploreError for bad-slug / missing-entry / missing-prompt / LLM /
    parse failures. Lower-level exceptions from the LLM call propagate as
    ExploreError(kind="llm").
    """
    if not SLUG_RE.match(slug):
        raise ExploreError(f"invalid slug: {slug!r}", kind="bad_slug")

    entry_path = wiki_dir / "catalogue" / f"{slug}.json"
    if not entry_path.is_file():
        raise ExploreError(
            f"entry not found: {_rel(entry_path)}",
            kind="not_found",
        )
    entry = json.loads(entry_path.read_text())
    log(f"[explore] slug={slug} title={entry.get('title')!r}")

    # Step 1: enrichment
    wiki_name = wiki_dir.name
    enrichment = None
    if fetch:
        path = run_fetch_wiki(wiki_name, slug, query, log=log)
        if path and path.is_file():
            enrichment = json.loads(path.read_text())
    else:
        cached = wiki_dir / "enrichments" / f"{slug}.json"
        if cached.is_file():
            log(f"[fetch] reusing {_rel(cached)}")
            enrichment = json.loads(cached.read_text())
        else:
            log(f"[fetch] no existing enrichment at {_rel(cached)}")

    # Step 2: LLM
    template_path = wiki_dir / "prompts" / "make_page.txt"
    if not template_path.is_file():
        raise ExploreError(
            f"prompt missing: {_rel(template_path)}",
            kind="config",
        )
    template = template_path.read_text()

    seed_payload = dict(entry)
    if enrichment is not None:
        seed_payload["enrichment"] = enrichment

    prompt = render_prompt(
        template,
        seed=json.dumps(seed_payload, indent=2, ensure_ascii=False),
    )
    wiki_config = json.loads((wiki_dir / "wiki.json").read_text())
    model = (wiki_config.get("models") or {}).get("make_page", DEFAULT_MODEL)
    log(f"[llm] prompt={len(prompt)} chars → {model}…")
    try:
        raw = run_llm(prompt, model=model)
    except Exception as e:
        raise ExploreError(f"LLM call failed: {e}", kind="llm") from e
    log(f"[llm] response={len(raw)} chars")

    try:
        payload = parse_json_blob(raw)
    except json.JSONDecodeError as e:
        log(f"[llm] non-JSON response: {e}")
        log(f"[llm] --- raw response ({len(raw)} chars) ---")
        log(raw)
        log("[llm] --- end raw ---")
        raise ExploreError(f"LLM returned non-JSON: {e}", kind="parse") from e

    if "facts" in payload:
        entry["facts"] = payload["facts"]
    if "links" in payload:
        entry["links"] = payload["links"]

    # Image path comes from the enrichment, not the LLM. The frontend reads
    # entry.image as a string and resolves it against the wiki root (the dev
    # server serves wikis/<wiki>/ at /), so we strip the wikis/<wiki>/ prefix.
    if enrichment:
        img = enrichment.get("image") or {}
        web_path = img.get("web_path") or img.get("local_path")
        if web_path:
            prefix = f"wikis/{wiki_name}/"
            if web_path.startswith(prefix):
                web_path = web_path[len(prefix):]
            entry["image"] = web_path

    entry["status"] = "explored"
    entry["updated"] = {"at": date.today().isoformat(), "by": "llm"}

    log(
        f"[merge] facts={len(entry.get('facts') or [])} "
        f"links={len(entry.get('links') or [])} "
        f"image={'yes' if entry.get('image') else 'no'}"
    )

    if write:
        with entry_path.open("w") as f:
            json.dump(entry, f, indent=2, ensure_ascii=False)
            f.write("\n")
        log(f"wrote {_rel(entry_path)}")

    return entry
