# Raymond

A multi-wiki platform for small, axis-driven reference works. See [project_vision.md](project_vision.md).

All commands assume [uv](https://docs.astral.sh/uv/) for dependency management. `uv run` provisions the venv from `pyproject.toml` on first use.

## Run a wiki

Dev mode (Flask, edit API enabled):

```bash
uv run python tools/dev_server.py <wiki>
# http://localhost:8765
```

Static mode (read-only bundle):

```bash
uv run python tools/export.py <wiki>
cd dist/<wiki> && python3 -m http.server 8765
```

## Rebuild the index

```bash
uv run python tools/build_index.py <wiki>
```

Writes `wikis/<wiki>/index.jsonl`. The dev server does this on startup and after edits.

## Add a new wiki

1. `mkdir -p wikis/<name>/{catalogue,pages,prompts,media}`
2. Write `wikis/<name>/wiki.json` and `axis.json`.
3. Write `prompts/make_list.txt` and `prompts/make_page.txt` using `{axis_id}` / `{seed}` placeholders.
4. `uv run python tools/dev_server.py <name>` and generate entries from the UI.
