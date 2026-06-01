"""Unified CLI for the data-atlas toolchain.

All subcommands operate on a wiki under wikis/<name>/ and share the same
core modules used by the Flask dev server, so behaviour stays in sync.

    uv run tools/atlas.py explore   --wiki megaprojects --slug aral-sea
    uv run tools/atlas.py fetch     --wiki megaprojects --slug aral-sea
    uv run tools/atlas.py generate  --wiki megaprojects --n 5 --axis domain=energy
    uv run tools/atlas.py reindex   --wiki megaprojects
    uv run tools/atlas.py serve     --wiki megaprojects --port 8765
"""

from __future__ import annotations

import json
import subprocess
import sys
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

import click

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

from build_index import resolve_wiki, write_index  # noqa: E402
from explore import ExploreError, explore_entry  # noqa: E402
from generate import GenerateError, generate_entries  # noqa: E402

# Map domain-error `kind` strings to process exit codes. Shared by every
# subcommand that surfaces an *Error so callers (scripts, Make targets) can
# branch on the cause without parsing stderr.
_EXIT_CODES = {
    "bad_slug": 2, "bad_input": 2, "not_found": 2, "config": 2,
    "parse": 3, "llm": 4,
}


def _wiki_dir(name: str) -> Path:
    try:
        return resolve_wiki(name)
    except SystemExit as e:
        raise click.BadParameter(str(e), param_hint="--wiki")


class _Tee:
    """File-like wrapper that writes to two streams (terminal + log file)."""

    def __init__(self, a, b):
        self._a, self._b = a, b

    def write(self, s: str) -> int:
        self._a.write(s)
        self._b.write(s)
        return len(s)

    def flush(self) -> None:
        self._a.flush()
        self._b.flush()


@contextmanager
def _tee_log(wiki_dir: Path, cmd: str):
    """Duplicate stdout/stderr into wikis/<wiki>/logs/<cmd>-<UTC>.log.

    The terminal still sees everything; the log file gets a stable copy
    plus a header (command, args, start/end timestamps, exit reason).
    """
    logs_dir = wiki_dir / "logs"
    logs_dir.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log_path = logs_dir / f"{cmd}-{stamp}.log"
    started = datetime.now(timezone.utc).isoformat(timespec="seconds")
    orig_out, orig_err = sys.stdout, sys.stderr
    with log_path.open("w") as fh:
        fh.write(f"# atlas {cmd}\n# argv: {' '.join(sys.argv)}\n# start: {started}\n\n")
        fh.flush()
        sys.stdout = _Tee(orig_out, fh)
        sys.stderr = _Tee(orig_err, fh)
        status = "ok"
        try:
            yield log_path
        except SystemExit as e:
            status = f"exit={e.code}"
            raise
        except BaseException as e:
            status = f"error={type(e).__name__}: {e}"
            raise
        finally:
            sys.stdout, sys.stderr = orig_out, orig_err
            ended = datetime.now(timezone.utc).isoformat(timespec="seconds")
            fh.write(f"\n# end: {ended}  status: {status}\n")
            click.echo(f"[atlas] log: {log_path}", err=True)


def _refresh_index(wiki_dir: Path) -> None:
    out = write_index(wiki_dir)
    n = sum(1 for _ in out.open())
    try:
        rel = out.relative_to(REPO_ROOT)
    except ValueError:
        rel = out
    click.echo(f"refreshed {rel} ({n} entries)")


@click.group(help=__doc__.splitlines()[0])
def cli() -> None:
    pass


# ── explore ────────────────────────────────────────────────────────────────────


@cli.command("explore", help="Promote an entry from 'generated' to 'explored'.")
@click.option("--wiki", required=True, help="Wiki name under wikis/.")
@click.option("--slug", required=True, help="Catalogue entry slug.")
@click.option("--query", default=None, help="Override the Wikipedia search query.")
@click.option("--skip-fetch", is_flag=True,
              help="Skip tools/fetch_wiki.py; reuse existing enrichment.")
@click.option("--dry-run", is_flag=True,
              help="Print the merged entry but don't write to disk.")
def explore_cmd(wiki: str, slug: str, query: str | None,
                skip_fetch: bool, dry_run: bool) -> None:
    wiki_dir = _wiki_dir(wiki)
    with _tee_log(wiki_dir, f"explore-{slug}"):
        try:
            entry = explore_entry(
                wiki_dir, slug,
                fetch=not skip_fetch, query=query, write=not dry_run,
                log=click.echo,
            )
        except ExploreError as e:
            click.echo(f"error ({e.kind}): {e}", err=True)
            sys.exit(_EXIT_CODES.get(e.kind, 1))

        if dry_run:
            click.echo("--- dry run, would write: ---")
            click.echo(json.dumps(entry, indent=2, ensure_ascii=False))
        else:
            _refresh_index(wiki_dir)


# ── fetch ──────────────────────────────────────────────────────────────────────


@cli.command("fetch", help="Fetch Wikipedia/Wikidata enrichment for an entry.")
@click.option("--wiki", required=True, help="Wiki name under wikis/.")
@click.option("--slug", required=True, help="Catalogue entry slug.")
@click.option("--query", default=None, help="Override the Wikipedia search query.")
@click.option("--no-image", is_flag=True, help="Skip downloading the lead image.")
@click.option("--no-shrink", is_flag=True, help="Skip shrink_image.sh on the image.")
@click.option("--no-wikidata", is_flag=True, help="Skip Wikidata facts.")
def fetch_cmd(wiki: str, slug: str, query: str | None,
              no_image: bool, no_shrink: bool, no_wikidata: bool) -> None:
    # fetch_wiki.py is a uv-script with its own dependencies (PEP 723);
    # invoke via `uv run --script` so its inline deps are honored. The
    # project venv (sys.executable) does not include `requests`.
    cmd = ["uv", "run", "--script", str(REPO_ROOT / "tools" / "fetch_wiki.py"),
           "--wiki", wiki, "--slug", slug]
    if query:
        cmd += ["--query", query]
    if no_image:
        cmd.append("--no-image")
    if no_shrink:
        cmd.append("--no-shrink")
    if no_wikidata:
        cmd.append("--no-wikidata")
    sys.exit(subprocess.call(cmd))


# ── generate ───────────────────────────────────────────────────────────────────


def _parse_axis(ctx, param, values):
    """Click callback: parse repeated --axis KEY=VALUE[,VALUE...] into a dict."""
    out: dict[str, str | list[str]] = {}
    for spec in values or ():
        if "=" not in spec:
            raise click.BadParameter(f"expected KEY=VALUE, got: {spec!r}",
                                     param=param)
        key, _, raw = spec.partition("=")
        key = key.strip()
        if not key:
            raise click.BadParameter(f"missing key: {spec!r}", param=param)
        if "," in raw:
            parts = [p.strip() for p in raw.split(",") if p.strip()]
            out[key] = parts if len(parts) > 1 else (parts[0] if parts else "")
        else:
            out[key] = raw.strip()
    return out


@cli.command("generate", help="Generate new catalogue entries for a wiki via LLM.")
@click.option("--wiki", required=True, help="Wiki name under wikis/.")
@click.option("--n", "n", type=int, default=5, show_default=True,
              help="Number of entries to request.")
@click.option("--axis", "axes", multiple=True, callback=_parse_axis,
              metavar="KEY=VALUE",
              help="Set a generation axis (repeatable; value may be comma-separated).")
@click.option("--existing", multiple=True, metavar="TITLE",
              help="Title to feed the prompt as already-known (repeatable).")
@click.option("--dry-run", is_flag=True,
              help="Print candidates but don't write to catalogue/ or rebuild index.")
def generate_cmd(wiki: str, n: int, axes: dict, existing: tuple[str, ...],
                 dry_run: bool) -> None:
    wiki_dir = _wiki_dir(wiki)
    with _tee_log(wiki_dir, "generate"):
        try:
            result = generate_entries(
                wiki_dir,
                axes=axes,
                n=n,
                existing=list(existing),
                write=not dry_run,
                log=click.echo,
            )
        except GenerateError as e:
            click.echo(f"error ({e.kind}): {e}", err=True)
            sys.exit(_EXIT_CODES.get(e.kind, 1))

        click.echo(json.dumps(result, indent=2, ensure_ascii=False))
        if not dry_run and result.get("written"):
            _refresh_index(wiki_dir)


# ── reindex ────────────────────────────────────────────────────────────────────


@cli.command("reindex", help="Rebuild wikis/<wiki>/index.jsonl from catalogue/.")
@click.option("--wiki", required=True, help="Wiki name under wikis/.")
def reindex_cmd(wiki: str) -> None:
    wiki_dir = _wiki_dir(wiki)
    with _tee_log(wiki_dir, "reindex"):
        _refresh_index(wiki_dir)


# ── serve ──────────────────────────────────────────────────────────────────────


@cli.command("serve", help="Run the Flask dev server for a wiki.")
@click.option("--wiki", required=True, help="Wiki name under wikis/.")
@click.option("--host", default="127.0.0.1", show_default=True)
@click.option("--port", type=int, default=8765, show_default=True)
def serve_cmd(wiki: str, host: str, port: int) -> None:
    # Import lazily — `serve` is the only command that needs flask + the
    # dev_server module, and importing dev_server runs Flask app construction
    # imports we don't want for the other subcommands.
    from dev_server import make_app

    wiki_dir = _wiki_dir(wiki)
    app = make_app(wiki_dir)
    click.echo(f"serving wiki {wiki_dir.name!r} at http://{host}:{port}/")
    app.run(host=host, port=port, debug=False)


if __name__ == "__main__":
    cli()
