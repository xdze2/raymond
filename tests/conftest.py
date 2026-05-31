"""Shared fixtures: a temporary wiki directory and a Flask test client.

Tests never touch real wikis under wikis/; everything happens in a tmp_path.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import dev_server


WIKI_CONFIG = {
    "id": "testwiki",
    "title": "Test Wiki",
    "wordmark": ["TEST"],
    "tagline": "Tests.",
    "placeholder_hint": "",
    "gen_axes": ["domain", "era"],
    "freeform_axes": [],
    "status_axis": "domain",
}

AXIS_CONFIG = {
    "axes": [
        {
            "id": "domain",
            "label": "Domain",
            "values": [
                {"id": "energy", "label": "Energy"},
                {"id": "transport", "label": "Transport"},
            ],
        },
        {
            "id": "era",
            "label": "Era",
            "values": [
                {"id": "modern", "label": "Modern"},
                {"id": "ancient", "label": "Ancient"},
            ],
        },
    ]
}

SEED_ENTRY = {
    "slug": "seed-one",
    "title": "Seed One",
    "summary": "A seed entry.",
    "status": "generated",
    "axes": {"domain": "energy", "era": "modern"},
}


@pytest.fixture
def wiki_dir(tmp_path: Path) -> Path:
    wd = tmp_path / "testwiki"
    (wd / "catalogue").mkdir(parents=True)
    (wd / "prompts").mkdir()
    (wd / "media").mkdir()
    (wd / "pages").mkdir()

    (wd / "wiki.json").write_text(json.dumps(WIKI_CONFIG))
    (wd / "axis.json").write_text(json.dumps(AXIS_CONFIG))
    (wd / "catalogue" / "seed-one.json").write_text(json.dumps(SEED_ENTRY))

    (wd / "prompts" / "make_list.txt").write_text(
        "Generate {n} entries for domain={domain} era={era}\nExisting:\n{existing}\n"
    )
    (wd / "prompts" / "make_page.txt").write_text("Explore: {seed}\n")
    return wd


@pytest.fixture
def client(wiki_dir: Path):
    app = dev_server.make_app(wiki_dir)
    app.config["TESTING"] = True
    return app.test_client()
