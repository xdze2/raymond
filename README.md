# Raymond

A multi-wiki platform for small, axis-driven reference works. Named after Raymond Queneau (Oulipo, *Cent mille milliards de poèmes*) — combinatorial exploration is the point.

Each wiki under `wikis/<name>/` is a self-contained atlas. See [project_vision.md](project_vision.md) for the concept.

## Layout

```
frontend/                # shared static frontend (one copy, all wikis)
wikis/
  mobility_innov/
    wiki.json            # title, wordmark, prompt axes
    axis.json            # axis definitions
    catalogue/           # one <slug>.json per entry
    pages/               # optional prose markdown (rare)
    media/               # images
    prompts/             # per-wiki LLM prompts
  data_atlas/
    ...
tools/
  build_index.py         # catalogue/*.json → wiki's index.jsonl
  dev_server.py          # Flask: serves frontend + a wiki, exposes edit API
  export.py              # dist/<wiki>/  standalone bundle
  gen_list.sh            # generate catalogue entries via Claude CLI
dist/                    # generated, gitignored
```

## Run a wiki locally

Two modes, same frontend.

**Dev mode** (Flask, edit enabled):

```bash
python tools/dev_server.py mobility_innov
# open http://localhost:8765
```

Unlocks: generate new entries, explore (promote) entries, edit in place.

**Static mode** (read-only) — first export, then serve the bundle:

```bash
python tools/export.py mobility_innov
cd dist/mobility_innov && python3 -m http.server 8765
# open http://localhost:8765
```

The exported `dist/<wiki>/` directory is self-contained and can be hosted anywhere.

## Rebuild the frontend index

```bash
python tools/build_index.py mobility_innov
```

Writes `wikis/mobility_innov/index.jsonl`. Run after manually editing catalogue files. The dev server does this automatically on startup and on writes.

## Generate catalogue entries

```bash
./tools/gen_list.sh mobility_innov electric individual short
# positional args = values for the axes declared in wiki.json's gen_axes
```

Or, in dev mode, click "Generate" in the UI.

## Add a new wiki

1. `mkdir -p wikis/<name>/{catalogue,pages,prompts,media}`
2. Create `wikis/<name>/wiki.json` (see `wikis/mobility_innov/wiki.json` for shape)
3. Create `wikis/<name>/axis.json` with your axes
4. Write `wikis/<name>/prompts/make_list.txt` using `{axis_id}` placeholders
5. Generate a first batch: `./tools/gen_list.sh <name> <axis values...>`
6. Open in the dev server: `python tools/dev_server.py <name>`
