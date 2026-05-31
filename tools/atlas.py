"""Unified CLI for the data-atlas toolchain.

All subcommands operate on a wiki under wikis/<name>/ and share the same
core modules used by the Flask dev server, so behaviour stays in sync.

    uv run tools/atlas.py explore  --wiki megaprojects --slug aral-sea
    uv run tools/atlas.py fetch    --wiki megaprojects --slug aral-sea
    uv run tools/atlas.py reindex  --wiki megaprojects
    uv run tools/atlas.py serve    --wiki megaprojects --port 8765
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import click

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

from build_index import resolve_wiki, write_index  # noqa: E402
from explore import ExploreError, explore_entry  # noqa: E402


def _wiki_dir(name: str) -> Path:
    try:
        return resolve_wiki(name)
    except SystemExit as e:
        raise click.BadParameter(str(e), param_hint="--wiki")


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
    try:
        entry = explore_entry(
            wiki_dir, slug,
            fetch=not skip_fetch, query=query, write=not dry_run,
            log=click.echo,
        )
    except ExploreError as e:
        click.echo(f"error ({e.kind}): {e}", err=True)
        sys.exit({"bad_slug": 2, "not_found": 2, "config": 2,
                  "parse": 3, "llm": 4}.get(e.kind, 1))

    if dry_run:
        click.echo("--- dry run, would write: ---")
        click.echo(json.dumps(entry, indent=2, ensure_ascii=False))


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
    # fetch_wiki.py is a uv-script with its own dependencies; shell out to
    # preserve that contract. When it's refactored into a module, swap this
    # for a direct import.
    cmd = [sys.executable, str(REPO_ROOT / "tools" / "fetch_wiki.py"),
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


# ── reindex ────────────────────────────────────────────────────────────────────


@cli.command("reindex", help="Rebuild wikis/<wiki>/index.jsonl from catalogue/.")
@click.option("--wiki", required=True, help="Wiki name under wikis/.")
def reindex_cmd(wiki: str) -> None:
    wiki_dir = _wiki_dir(wiki)
    out = write_index(wiki_dir)
    n = sum(1 for _ in out.open())
    try:
        rel = out.relative_to(REPO_ROOT)
    except ValueError:
        rel = out
    click.echo(f"wrote {rel} ({n} entries)")


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
