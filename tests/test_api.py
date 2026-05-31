"""Tests for the dev_server Flask API: health, validation, edit endpoints.

The LLM call (`run_llm`) is monkeypatched everywhere — these tests never
shell out.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import dev_server
import explore
import generate


# ── health & static passthrough ────────────────────────────────────────────────


def test_health(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.get_json() == {"mode": "dev", "wiki": "testwiki"}


def test_index_jsonl_passthrough(client, wiki_dir: Path):
    res = client.get("/index.jsonl")
    assert res.status_code == 200
    lines = [l for l in res.data.decode().splitlines() if l.strip()]
    assert len(lines) == 1
    assert json.loads(lines[0])["slug"] == "seed-one"


def test_wiki_and_axis_passthrough(client):
    assert client.get("/wiki.json").status_code == 200
    assert client.get("/axis.json").status_code == 200


def test_frontend_index_served(client):
    res = client.get("/")
    assert res.status_code == 200
    assert b"<html" in res.data.lower()


def test_responses_disable_caching(client):
    # Browser cached stale index.jsonl after backend rewrites; dev server
    # must serve everything with Cache-Control: no-store.
    for path in ("/", "/index.jsonl", "/wiki.json", "/axis.json"):
        res = client.get(path)
        assert res.status_code == 200, path
        assert res.headers.get("Cache-Control") == "no-store", path


def test_path_traversal_blocked(client):
    res = client.get("/..%2Fpyproject.toml")
    # flask normalises URL, so this becomes /pyproject.toml → 404 against frontend
    assert res.status_code == 404


# ── /api/reindex ───────────────────────────────────────────────────────────────


def test_reindex(client, wiki_dir: Path):
    # add a second entry directly on disk
    (wiki_dir / "catalogue" / "extra.json").write_text(
        json.dumps({"slug": "extra", "title": "Extra", "axes": {}})
    )
    res = client.post("/api/reindex")
    assert res.status_code == 200
    assert res.get_json() == {"ok": True, "entries": 2}
    # index.jsonl now reflects both
    index_lines = (wiki_dir / "index.jsonl").read_text().strip().splitlines()
    slugs = {json.loads(l)["slug"] for l in index_lines}
    assert slugs == {"seed-one", "extra"}


# ── /api/generate validation ──────────────────────────────────────────────────


def test_generate_no_axes_allowed(client, monkeypatch):
    # With "search more" semantics, no filters means "any" on every axis.
    monkeypatch.setattr(generate, "run_llm", lambda p, **kw: '{"slug": "x", "title": "X"}\n')
    res = client.post("/api/generate", json={"n": 1})
    assert res.status_code == 200


def test_generate_partial_axes_allowed(client, monkeypatch):
    # Missing axes are fine; specified ones render normally.
    captured = {}

    def fake(prompt, **kw):
        captured["prompt"] = prompt
        return '{"slug": "p", "title": "P"}\n'

    monkeypatch.setattr(generate, "run_llm", fake)
    res = client.post(
        "/api/generate",
        json={"axes": {"domain": "energy"}, "n": 1},
    )
    assert res.status_code == 200
    # the unspecified axis renders as "any"
    assert "any" in captured["prompt"]


def test_generate_rejects_non_object_axes(client):
    res = client.post("/api/generate", json={"axes": "not-a-dict", "n": 1})
    assert res.status_code == 400


def test_generate_passes_existing_titles(client, monkeypatch):
    captured = {}

    def fake(prompt, **kw):
        captured["prompt"] = prompt
        return '{"slug": "n", "title": "N"}\n'

    monkeypatch.setattr(generate, "run_llm", fake)
    res = client.post(
        "/api/generate",
        json={
            "axes": {"domain": "energy"},
            "n": 1,
            "existing": ["Hoover Dam", "Three Gorges"],
        },
    )
    assert res.status_code == 200
    assert "Hoover Dam" in captured["prompt"]
    assert "Three Gorges" in captured["prompt"]


def test_generate_writes_entries(client, wiki_dir: Path, monkeypatch):
    fake_jsonl = (
        '{"slug": "new-one", "title": "New One", "summary": "first"}\n'
        '{"slug": "new-two", "title": "New Two", "summary": "second"}\n'
    )
    monkeypatch.setattr(generate, "run_llm", lambda prompt, **kw: fake_jsonl)

    res = client.post(
        "/api/generate",
        json={"axes": {"domain": "energy", "era": "modern"}, "n": 2},
    )
    assert res.status_code == 200
    data = res.get_json()
    assert set(data["written"]) == {"new-one", "new-two"}
    assert data["skipped"] == []

    # files written with merged axes + status=generated + created stamp
    entry = json.loads((wiki_dir / "catalogue" / "new-one.json").read_text())
    assert entry["axes"] == {"domain": "energy", "era": "modern"}
    assert entry["status"] == "generated"
    assert entry["created"]["by"].startswith("llm:")


def test_generate_skips_existing(client, wiki_dir: Path, monkeypatch):
    fake_jsonl = '{"slug": "seed-one", "title": "Dupe"}\n'
    monkeypatch.setattr(generate, "run_llm", lambda prompt, **kw: fake_jsonl)

    res = client.post(
        "/api/generate",
        json={"axes": {"domain": "energy", "era": "modern"}, "n": 1},
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data["written"] == []
    assert data["skipped"][0]["slug"] == "seed-one"


def test_generate_skips_invalid_slug(client, monkeypatch):
    fake_jsonl = '{"slug": "Has Spaces", "title": "Bad"}\n'
    monkeypatch.setattr(generate, "run_llm", lambda prompt, **kw: fake_jsonl)

    res = client.post(
        "/api/generate",
        json={"axes": {"domain": "energy", "era": "modern"}, "n": 1},
    )
    assert res.status_code == 200
    assert res.get_json()["written"] == []


def test_generate_tolerates_code_fences(client, wiki_dir: Path, monkeypatch):
    fake = (
        "```jsonl\n"
        '{"slug": "fenced", "title": "Fenced"}\n'
        "```\n"
    )
    monkeypatch.setattr(generate, "run_llm", lambda p, **kw: fake)
    res = client.post(
        "/api/generate",
        json={"axes": {"domain": "energy", "era": "modern"}, "n": 1},
    )
    assert res.status_code == 200
    assert res.get_json()["written"] == ["fenced"]


# ── /api/entries/<slug>/explore ───────────────────────────────────────────────


def test_explore_unknown_slug_404(client):
    res = client.post("/api/entries/nope/explore")
    assert res.status_code == 404


def test_explore_bad_slug_400(client):
    res = client.post("/api/entries/BAD%20SLUG/explore")
    assert res.status_code == 400


def test_explore_promotes_to_explored(client, wiki_dir: Path, monkeypatch):
    payload = {
        "facts": [{"label": "Built", "value": "1969"}],
        "links": [{"label": "wiki", "url": "https://x"}],
    }
    monkeypatch.setattr(explore, "run_llm", lambda p, **kw: json.dumps(payload))

    res = client.post("/api/entries/seed-one/explore?fetch=0")
    assert res.status_code == 200
    body = res.get_json()
    assert body["status"] == "explored"
    assert body["facts"] == payload["facts"]
    assert body["links"] == payload["links"]
    assert body["updated"]["by"].startswith("llm:")

    # persisted on disk
    on_disk = json.loads((wiki_dir / "catalogue" / "seed-one.json").read_text())
    assert on_disk["status"] == "explored"


def test_explore_handles_fenced_json(client, monkeypatch):
    raw = "```json\n" + json.dumps({"facts": [{"label": "a", "value": "b"}]}) + "\n```"
    monkeypatch.setattr(explore, "run_llm", lambda p, **kw: raw)
    res = client.post("/api/entries/seed-one/explore?fetch=0")
    assert res.status_code == 200
    assert res.get_json()["facts"] == [{"label": "a", "value": "b"}]


def test_explore_rejects_non_json(client, monkeypatch):
    monkeypatch.setattr(explore, "run_llm", lambda p, **kw: "not json at all")
    res = client.post("/api/entries/seed-one/explore?fetch=0")
    assert res.status_code == 502


def test_explore_llm_failure(client, monkeypatch):
    def boom(_, **kw):
        raise RuntimeError("model exploded")

    monkeypatch.setattr(explore, "run_llm", boom)
    res = client.post("/api/entries/seed-one/explore?fetch=0")
    assert res.status_code == 502


# ── PUT /api/entries/<slug> ───────────────────────────────────────────────────


def test_put_merges_and_stamps(client, wiki_dir: Path):
    res = client.put(
        "/api/entries/seed-one",
        json={"summary": "edited summary", "facts": [{"label": "L", "value": "V"}]},
    )
    assert res.status_code == 200
    body = res.get_json()
    # merged fields applied
    assert body["summary"] == "edited summary"
    assert body["facts"] == [{"label": "L", "value": "V"}]
    # untouched fields preserved
    assert body["title"] == "Seed One"
    assert body["axes"] == {"domain": "energy", "era": "modern"}
    # stamp by user
    assert body["updated"]["by"] == "user"


def test_put_rejects_slug_mismatch(client):
    res = client.put(
        "/api/entries/seed-one",
        json={"slug": "different", "summary": "x"},
    )
    assert res.status_code == 400


def test_put_unknown_slug_404(client):
    res = client.put("/api/entries/nope", json={"summary": "x"})
    assert res.status_code == 404


def test_put_rejects_non_object_body(client):
    res = client.put("/api/entries/seed-one", data="null", content_type="application/json")
    assert res.status_code == 400
