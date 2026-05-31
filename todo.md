# TODO

## Next up — LLM cost/speed + batch filling

Goal: make generation cheaper and faster, give the user real-time feedback, and grow the wiki without one-click-at-a-time tedium. Ordered cheapest-first; each step independently shippable. Keep the stack simple — plain Flask + vanilla JS frontend, no WebSockets, no framework rewrite.

### A — Usage logging
- [ ] Append one JSONL record per LLM call to `wikis/<wiki>/llm_calls.jsonl`: timestamp, model, prompt name, input/output tokens, latency, est. cost, slug (if any).
- [ ] Hook it into `tools/llm.py` so every provider goes through the same log path.
- [ ] `.gitignore` the log file.

### B — Provider abstraction in `tools/llm.py` ✅
- [x] Refactor `run_claude` → `run_llm(prompt, model=...)` with a thin dispatcher. Model strings are `"<provider>:<name>"`.
- [x] Keep current `claude --print` path as one backend; `run_claude` kept as a back-compat alias in `llm.py`.
- [x] Tests patch `dev_server.run_llm` / `explore.run_llm` with `lambda p, **kw: ...` to swallow the `model=` kwarg. `CLAUDE.md` updated.

### C — Optimistic UI + elapsed counter
- [ ] On `generate` / `explore` click: immediately render the entry/card in a "generating…" state with a live elapsed-seconds counter.
- [ ] Disable the trigger button, show a cancel affordance (even if cancel is best-effort).
- [ ] On error, surface the message inline (not just console).

### D — Mistral via API
- [x] Add a Mistral backend to `run_llm` (API key from env, lazy SDK init).
- [x] Per-prompt config to pick model — `wiki.json` has a `models: {make_list, make_page}` map; routes read it and pass through to `run_llm`.
- [x] Real end-to-end check: `mistral:mistral-small-latest` on `/api/generate` returned 3 valid entries in 4.6s. Required two fixes along the way:
  - `tools/env_config.py` loads `.env` (no `python-dotenv` dep); `mistral.py` reads the key from it.
  - Mistral's `response_format=json_object` forces a single wrapper object, so `make_list.txt` now asks for `{"entries": [...]}` and `_parse_jsonl` accepts wrapper-object / array / JSONL.
- [ ] Watch axis drift: one of the 3 test entries came back with `domain=infrastructure` despite `domain=energy` being requested. Track this in the eval below.
- [ ] Tiny eval: regenerate 5 existing entries with Mistral, diff against current, decide where it's good enough.

### D.5 — DDG grounding for `explore`
- [ ] Wire `tools/ddg.py` into `explore_entry`: search on entry title, pass top N snippets into `make_page.txt` as a `{sources}` block, instruct the LLM to only state facts present in sources and populate `links[]` with the URLs it used.
- [ ] Add `{sources}` placeholder to `wikis/megaprojects/prompts/make_page.txt`.
- [ ] Behind a per-wiki flag (e.g. `wiki.json` `grounding: "ddg"` / `"none"`) so it's A/B-able.
- [ ] Skip if existing enrichments file is present (already grounded via `fetch_wiki.py`).

### E — Batch generation (CLI, not a route)
- [ ] `tools/batch_generate.py <wiki> [--axes ...] [--n N]` — runs `make_list` then `make_page` for each new slug, writes to `catalogue/`, rebuilds index.
- [ ] Dedup against existing slugs; skip-or-retry on LLM errors with backoff.
- [ ] Decision needed: seed list source — curated input file vs. LLM-proposed neighbors of existing entries. Start with curated.

### F — SSE streaming (only if C isn't enough)
- [ ] Add `text/event-stream` variants of `/api/generate` and `/api/entries/<slug>/explore` for prose fields.
- [ ] Structured JSON outputs stay non-streaming (can't parse partial JSON cleanly).
- [ ] Skip entirely if the optimistic UI already feels good.

---

## Migration TODO (done)

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

## Step 9 — Flask edit endpoints ✅

Goal: wire the existing CLI tools into the frontend.

- [x] `POST /api/generate` — body: `{ axes: {...}, n: int }`. Renders `prompts/make_list.txt`, shells out to `claude --print`, parses JSONL, writes one `catalogue/<slug>.json` per entry, re-runs `build_index`, returns `{written, skipped}`.
- [x] `POST /api/entries/<slug>/explore` — renders `prompts/make_page.txt` with seed entry, calls LLM, merges `facts`/`links`/`image`, flips status to `explored`, stamps `updated`.
- [x] `PUT /api/entries/<slug>` — merges body over existing entry, stamps `updated: {by: "user"}`.
- [x] `POST /api/reindex` — rebuilds `index.jsonl`, returns entry count.
- [x] `tools/llm.py` added — thin `claude` CLI wrapper + `{placeholder}` renderer.
- [x] `wikis/megaprojects/prompts/make_page.txt` added — emits the new `{facts, links}` JSON shape (not the old markdown page format).
- [x] Validation paths verified via curl (400/404 on bad input, PUT round-trip preserves untouched fields). LLM-backed `/generate` and `/explore` are wired but not yet end-to-end-tested with a real model call.

---

## Step 10 — Edit-mode UI in the frontend ✅

Goal: frontend probes `/api/health`; if present, shows edit controls.

- [x] On load, frontend fetches `./api/health`. If 200, sets `editMode` and `body.edit-mode`.
- [x] In edit mode: "+ generate" button in grid header (appears when each `gen_axes` filter has exactly one value), "explore →" button on `generated` entries in the modal, "edit" button (raw JSON editor) on every entry in the modal.
- [x] In static mode: `.edit-only` elements hidden via CSS, `/api/health` probe silently fails.
- [x] pytest suite added under `tests/` (22 tests) covering health, passthrough, validation, generate/explore/edit endpoints with `run_claude` monkeypatched.
- [x] `make_app()` now writes `index.jsonl` on startup (was only done by `main()`), so any consumer of the Flask app gets a populated index.

**Verify:** `.venv/bin/python -m pytest tests/` → 22 passed.

---

## Parked (revisit later)

- Markdown notes per entry (lightweight successor to `pages/*.md`)
- Suggested fact keys declared in `wiki.json`
- Hierarchical / node-type axes
- Landing page listing all wikis
- Multi-wiki dev server mode
