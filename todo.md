# Migration TODO

Refactor toward: per-entry JSON files, shared frontend, build/export/dev scripts under `tools/`. Each step is independently verifiable.

---

## Step 1 — Per-entry catalogue files + `build_index.py`

Goal: replace JSONL catalogue with one JSON file per entry, generated index for the frontend.

- [ ] Create `tools/build_index.py` exposing:
  - `build_index(wiki_dir: Path) -> list[dict]` — read `catalogue/*.json`, return merged list
  - `write_index(wiki_dir: Path) -> Path` — write `<wiki_dir>/index.jsonl`
  - CLI: `python tools/build_index.py <wiki>`
- [ ] Write a one-shot migration script that splits existing `catalogue/list_*.jsonl` into `catalogue/<slug>.json`, adding `status: "generated"` and a `created` block to each.
- [ ] Run migration on `mobility_innov`. Verify: `ls wikis/mobility_innov/catalogue/*.json` shows one file per entry; no `.jsonl` files remain.
- [ ] Run `python tools/build_index.py mobility_innov`. Verify: `wikis/mobility_innov/index.jsonl` exists, line count matches entry count.
- [ ] Add `index.jsonl` and `dist/` to `.gitignore`.

**Verify:** `wc -l wikis/mobility_innov/index.jsonl` equals `ls wikis/mobility_innov/catalogue/*.json | wc -l`.

---

## Step 2 — Update frontend to load `index.jsonl`

Goal: frontend fetches a single index file via relative paths.

- [ ] Update `wikis/mobility_innov/frontend/app.js` (or wherever the fetch lives) to load `./index.jsonl` instead of multiple files from `catalogue/index.json`.
- [ ] Remove dependency on `catalogue/index.json` and `pages/index.json` from the frontend code.
- [ ] Replace `has_page` checks with `status === "explored"` checks.

**Verify:** open `http://localhost:8765/wikis/mobility_innov/frontend/index.html`, all entries render, filters work, no console errors.

---

## Step 3 — Promote frontend to repo root

Goal: one shared `frontend/` directory, paths are all relative.

- [ ] `mkdir frontend/` at repo root.
- [ ] Move `wikis/mobility_innov/frontend/*` to `frontend/`.
- [ ] Delete `wikis/*/frontend/` directories.
- [ ] Confirm `frontend/app.js` uses only relative paths (`./wiki.json`, `./axis.json`, `./index.jsonl`, `./media/...`, `./pages/...`).

**Verify:** `frontend/` exists at root; no `wikis/*/frontend/` remains; `grep -r "wikis/" frontend/` returns nothing.

---

## Step 4 — `tools/dev_server.py` (Flask, read-only first)

Goal: serve the shared frontend over a chosen wiki's files. No edit endpoints yet.

- [ ] Create `tools/dev_server.py`. Usage: `python tools/dev_server.py <wiki> [--port 8765]`.
- [ ] Server mounts `wikis/<wiki>/` and `frontend/` so the frontend can fetch `./wiki.json`, `./index.jsonl`, etc. from the same origin.
- [ ] On startup, call `build_index.write_index()` so `index.jsonl` is fresh.
- [ ] Add `GET /api/health` returning `{ "mode": "dev", "wiki": "<name>" }`.
- [ ] Add `tools/__init__.py` so imports resolve.

**Verify:** `python tools/dev_server.py mobility_innov`, open `http://localhost:8765/`, wiki renders identically to step 2.

---

## Step 5 — `tools/export.py` (standalone static bundle)

Goal: produce a self-contained `dist/<wiki>/` directory.

- [ ] Create `tools/export.py`. Usage: `python tools/export.py <wiki>`.
- [ ] Copy `frontend/*` into `dist/<wiki>/`.
- [ ] Copy `wikis/<wiki>/{wiki.json,axis.json,media/,pages/}` into `dist/<wiki>/`.
- [ ] Call `build_index.write_index()` writing into `dist/<wiki>/index.jsonl`.
- [ ] Do NOT copy `catalogue/` or `prompts/` (not needed at runtime).

**Verify:** `python tools/export.py mobility_innov && cd dist/mobility_innov && python3 -m http.server 8766`, open browser, wiki renders identically.

---

## Step 6 — Move existing tools into `tools/`

Goal: clean repo root.

- [ ] Move `gen_list.sh` → `tools/gen_list.sh` (or port to `tools/gen_entries.py`).
- [ ] Delete `update_index.sh` (folded into `build_index.py`).
- [ ] Update any references in README/docs.

**Verify:** repo root contains only `frontend/`, `wikis/`, `tools/`, `dist/` (gitignored), `README.md`, `project_vision.md`, `todo.md`, `.gitignore`.

---

## Step 7 — Entry status: `generated` vs `explored`

Goal: replace `has_page` with a `status` field on every entry.

- [ ] In `build_index.py`, ensure every emitted entry has `status` (default `"generated"`).
- [ ] Frontend: visually distinguish `explored` entries in the card grid (badge, border, or icon).
- [ ] Manually promote 2–3 existing entries to `status: "explored"` and fill in `facts`, `links`, `image` to validate the shape.

**Verify:** the explored entries render their facts/links in the modal; generated entries show only summary + axes.

---

## Step 8 — Entry shape: `facts`, `links`, `image`, `created`, `updated`

Goal: standardize the entry file format.

- [ ] Document the entry schema in `project_vision.md`.
- [ ] Update the modal view to render:
  - `facts[]` as a small label/value list
  - `links[]` as a row of labeled link chips
  - `image` if present
- [ ] Keep modal minimal — no prose, no markdown notes (parked for later).

**Verify:** modal for an `explored` entry shows facts + links + image, nothing else.

---

## Step 9 — Flask edit endpoints

Goal: wire the existing CLI tools into the frontend.

- [ ] `POST /api/generate` — body: `{ axes: {...}, n: int }`. Wraps catalogue generation; writes new `catalogue/<slug>.json` files; re-runs `build_index`; returns new slugs.
- [ ] `POST /api/entries/<slug>/explore` — promotes `generated` → `explored`; LLM fills `facts`, `links`, possibly `image`; writes file; returns updated entry.
- [ ] `PUT /api/entries/<slug>` — save manual edits; updates `updated` block.
- [ ] `POST /api/reindex` — force rebuild of `index.jsonl`.

**Verify each:** call from `curl`, file appears/changes on disk, response payload matches.

---

## Step 10 — Edit-mode UI in the frontend

Goal: frontend probes `/api/health`; if present, shows edit controls.

- [ ] On load, frontend fetches `/api/health`. If 200, set `editMode = true`.
- [ ] In edit mode: add "Generate similar" button on axis combinations, "Explore" button on `generated` entries, "Edit" button in the modal.
- [ ] In static mode (exported bundle): controls hidden, identical look to step 2.

**Verify:** `python tools/dev_server.py mobility_innov` shows edit controls; exported bundle from step 5 does not.

---

## Parked (revisit later)

- Markdown notes per entry (lightweight successor to `pages/*.md`)
- Suggested fact keys declared in `wiki.json`
- Hierarchical / node-type axes
- Landing page listing all wikis
- Multi-wiki dev server mode
