"""Core: generate new "generated"-status catalogue entries via LLM.

Shared by the CLI (`tools/generate_entries.py`) and the Flask route
(`/api/generate` in `tools/dev_server.py`). Keep all prompt rendering,
LLM call, parsing, and disk write in here so both interfaces stay in sync.
"""

from __future__ import annotations

import json
import re
import time
from datetime import date
from pathlib import Path
from typing import Callable

from llm import DEFAULT_MODEL, render_prompt, run_llm

SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")

Logger = Callable[[str], None]


class GenerateError(Exception):
    """Recoverable generate failure. `kind` lets callers map to HTTP status."""

    def __init__(self, message: str, *, kind: str = "internal"):
        super().__init__(message)
        self.kind = kind


def _today() -> str:
    return date.today().isoformat()


def _write_entry(wiki_dir: Path, entry: dict) -> Path:
    slug = entry["slug"]
    if not SLUG_RE.match(slug):
        raise ValueError(f"invalid slug: {slug!r}")
    path = wiki_dir / "catalogue" / f"{slug}.json"
    with path.open("w") as f:
        json.dump(entry, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return path


def parse_jsonl(text: str) -> list[dict]:
    """Parse LLM output as JSONL, tolerating ```fences and wrapper objects."""
    # Strip ```json fences if present, then try whole-text JSON first
    # (Mistral's json_object mode returns one wrapper object, not JSONL).
    stripped = "\n".join(
        line for line in text.splitlines() if not line.strip().startswith("```")
    ).strip()
    if stripped:
        try:
            obj = json.loads(stripped)
        except json.JSONDecodeError:
            obj = None
        if isinstance(obj, list):
            return [e for e in obj if isinstance(e, dict)]
        if isinstance(obj, dict):
            for key in ("entries", "candidates", "items", "results"):
                v = obj.get(key)
                if isinstance(v, list):
                    return [e for e in v if isinstance(e, dict)]
            if "slug" in obj:
                return [obj]

    out: list[dict] = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("```"):
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def generate_entries(
    wiki_dir: Path,
    *,
    axes: dict | None = None,
    n: int = 5,
    existing: list[str] | None = None,
    write: bool = True,
    log: Logger = print,
) -> dict:
    """Generate up to `n` new entries with status="generated".

    Returns {"written": [slug, ...], "skipped": [{...}, ...]}.

    Side effects (when `write=True`): writes catalogue/<slug>.json for each
    accepted candidate.

    Raises GenerateError for bad inputs / missing prompt / LLM failures.
    """
    axes = axes or {}
    existing = existing or []
    if not isinstance(axes, dict):
        raise GenerateError("axes must be an object", kind="bad_input")
    if not isinstance(existing, list):
        raise GenerateError("existing must be a list", kind="bad_input")

    with (wiki_dir / "wiki.json").open() as f:
        config = json.load(f)

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

    template_path = wiki_dir / "prompts" / "make_list.txt"
    if not template_path.is_file():
        raise GenerateError("make_list.txt prompt missing", kind="config")
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
    log(f"[generate] n={n} existing={len(existing)} axes: {axes_summary}")
    log(f"[generate] prompt={len(prompt)} chars → {model}…")

    t0 = time.monotonic()
    try:
        raw = run_llm(prompt, model=model)
    except Exception as e:
        log(f"[generate] LLM call failed after {time.monotonic() - t0:.1f}s: {e}")
        raise GenerateError(f"LLM call failed: {e}", kind="llm") from e
    dt = time.monotonic() - t0
    log(f"[generate] {model} returned {len(raw)} chars in {dt:.1f}s")

    candidates = parse_jsonl(raw)
    log(f"[generate] parsed {len(candidates)} candidate entries")

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
        entry["created"] = {"at": _today(), "by": f"llm:{model}"}
        if write:
            _write_entry(wiki_dir, entry)
        written.append(slug)

    log(
        f"[generate] wrote {len(written)} ({', '.join(written) or '—'}), "
        f"skipped {len(skipped)}"
    )

    return {"written": written, "skipped": skipped}
