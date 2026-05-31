# Migration TODO

Refactor toward: per-entry JSON files, shared frontend, build/export/dev scripts under `tools/`. Each step is independently verifiable.

**Note (2026-05-31):** old wikis (`mobility_innov`, `data_atlas`) moved to `archive/`. The new structure was built fresh against a new wiki, `megaprojects`. Steps 1–8 below are checked off accordingly — no data was ported; the new shape is exercised by 5 hand-written seed entries.

---

## Step 1 — Per-entry catalogue files + `build_index.py` ✅

Goal: replace JSONL catalogue with one JSON file per entry, generated index for the frontend.

- [x] Create `tools/build_index.py` exposing `build_index()`, `write_index()`, CLI.
- [x] ~~One-shot migration script~~ — skipped, no data to port.
- [x] `ls wikis/megaprojects/catalogue/*.json` → 5 files, no `.jsonl` in `catalogue/`.
- [x] `python tools/build_index.py megaprojects` → `index.jsonl` exists, 5 lines.
- [x] `.gitignore` covers `wikis/*/index.jsonl` and `dist/`.

---

## Step 2 — Update frontend to load `index.jsonl` ✅

Goal: frontend fetches a single index file via relative paths.

- [x] Frontend loads `./index.jsonl` (single fetch, no catalogue/pages indirection).
- [x] No `catalogue/index.json` or `pages/index.json` dependency.
- [x] `has_page` replaced with `status === "explored"` checks.

---

## Step 3 — Promote frontend to repo root ✅

Goal: one shared `frontend/` directory, paths are all relative.

- [x] `frontend/` created at repo root.
- [x] Old per-wiki `frontend/` lives only in `archive/`.
- [x] All paths in `frontend/index.html` are relative (`./wiki.json`, `./axis.json`, `./index.jsonl`, `./media/...`).

---

## Step 4 — `tools/dev_server.py` (Flask, read-only first) ✅

Goal: serve the shared frontend over a chosen wiki's files. No edit endpoints yet.

- [x] `tools/dev_server.py` — usage `python tools/dev_server.py <wiki> [--port N]`.
- [x] Layered routing: `wiki.json` / `axis.json` / `index.jsonl` / `media/*` / `pages/*` from the wiki dir; everything else from `frontend/`.
- [x] `write_index()` runs on startup.
- [x] `GET /api/health` → `{"mode": "dev", "wiki": "<name>"}`.
- [x] `tools/__init__.py` in place.

---

## Step 5 — `tools/export.py` (standalone static bundle) ✅

Goal: produce a self-contained `dist/<wiki>/` directory.

- [x] `tools/export.py` — usage `python tools/export.py <wiki>`.
- [x] Copies `frontend/*` + `wiki.json` + `axis.json` + `media/` + `pages/` (when non-empty).
- [x] Writes fresh `index.jsonl` into the bundle.
- [x] Skips `catalogue/` and `prompts/`.
- [x] Verified: `dist/megaprojects/` served by `python3 -m http.server` renders identically; `/api/health` 404.

---

## Step 6 — Move existing tools into `tools/` ✅ (partial)

Goal: clean repo root.

- [x] Old `gen_list.sh` archived (lived in repo root, now in `archive/`'s historical context). Replacement (`gen_entries.py`) will land with Step 9.
- [x] Old `update_index.sh` folded into `build_index.py`.
- [ ] Repo root still has the legacy `gen_list.sh` and `update_index.sh` shims — sweep them when the new generation flow lands.

---

## Step 7 — Entry status: `generated` vs `explored` ✅

Goal: replace `has_page` with a `status` field on every entry.

- [x] `build_index.py` defaults missing `status` to `"generated"`.
- [x] Cards: explored = solid border / full opacity; generated = dashed border / 0.72 opacity.
- [x] All 5 seed entries are `explored` (Aral Sea, Atlantropa, Ryugyong, Biosphere 2, Fordlândia).

---

## Step 8 — Entry shape: `facts`, `links`, `image`, `created`, `updated` ✅

Goal: standardize the entry file format.

- [x] Schema already documented in `project_vision.md` (pre-refactor).
- [x] Modal renders `facts[]` as a 2-col label/value grid, `links[]` as a chip row, `image` above when present.
- [x] No prose / markdown in the modal — clean facts/links/image only.

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
