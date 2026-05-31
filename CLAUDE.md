# Notes for Claude

## Tests

Tests live in `tests/` and target the Flask API in `tools/dev_server.py`.

### Running

```bash
uv sync --extra dev     # once
uv run pytest           # all tests
uv run pytest tests/test_api.py::test_explore_promotes_to_explored -v
```

`pyproject.toml` sets `pythonpath = ["tools"]` so tests can `import dev_server`,
`import build_index`, `import llm` directly without packaging the `tools/` dir.

### Fixtures (`tests/conftest.py`)

- `wiki_dir` — a `tmp_path`-rooted wiki with `wiki.json`, `axis.json`, one seed
  entry in `catalogue/`, and stub prompt templates. Tests **never** touch real
  wikis under `wikis/`.
- `client` — a Flask test client built from `dev_server.make_app(wiki_dir)`.
  `make_app()` writes `index.jsonl` on construction, so `/index.jsonl` is
  immediately serveable.

### Mocking the LLM

`dev_server.run_llm` is imported by name (`from llm import run_llm`), so patch
it on the `dev_server` module (or `explore` module for the explore route), not
on `llm`:

```python
monkeypatch.setattr(dev_server, "run_llm", lambda prompt, **kw: '{"facts": []}')
monkeypatch.setattr(explore, "run_llm", lambda prompt, **kw: '{"facts": []}')
```

The `**kw` swallows the `model=` kwarg that callers pass through from
`wiki.json`'s `models` map. Patching `llm.run_llm` would not take effect —
`dev_server` / `explore` already hold a reference to the original function.

### What's covered

- Static passthrough: `/`, `/style.css`, `/wiki.json`, `/axis.json`, `/index.jsonl`
- `/api/health` — shape + values
- `/api/reindex` — count after adding a file directly to `catalogue/`
- `/api/generate` — missing body, missing required axis, happy path, dedup against
  existing slugs, invalid-slug rejection, code-fence tolerance
- `/api/entries/<slug>/explore` — 404, 400 (bad slug), happy path (status flip +
  `updated.by = "llm"`), fenced JSON, non-JSON 502, LLM exception 502
- `PUT /api/entries/<slug>` — merge + `updated.by = "user"`, slug mismatch 400,
  unknown slug 404, non-object body 400

### When adding a feature

1. Add the route handler in `tools/dev_server.py`.
2. Add tests in `tests/test_api.py` covering: happy path + validation errors +
   (if it calls the LLM) a `monkeypatch.setattr(dev_server, "run_llm", ...)`
   stub for success and one for failure.
3. Run `uv run pytest` — keep the suite green before moving on.

### Out of scope

No frontend / browser tests yet. The edit-mode UI in `frontend/index.html` is
exercised by hand against `tools/dev_server.py`. If JS logic gets non-trivial,
consider Playwright over the test client.
