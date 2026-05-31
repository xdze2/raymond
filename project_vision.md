# Raymond — Project Vision

Named after Raymond Queneau — Oulipo, *Cent mille milliards de poèmes*, *Exercices de style*. Combinatorial generation under constraint, where the grid produces what no single author would write unprompted. That's the design north star.

## What It Is

A platform for building small, focused reference works. Each wiki is a TVTropes-style atlas of a single subject: every entry sits in a multi-axis space that makes entries comparable, browsable, and discoverable through combinatorial exploration.

A wiki is **not an encyclopedia**. The point is not exhaustive prose articles — it is the *space* of entries, navigated through axis combinations. An entry is a card in a grid first, a page second (or never).

The closest analogies: TVTropes (a taxonomy that becomes a lens), and a faceted catalog raised to a curation discipline. You arrive at the wiki through an axis combination — *what electric, individual-scale, short-range mobility innovations exist?* — and the answer is the visible cards.

Current wikis in this repo:

- **`mobility_innov`** — mobility innovations (active development)
- **`data_atlas`** — datasets: what exists, what's buried, what's missing

New wikis are added by dropping a folder under `wikis/<name>/`.

## The Axis System

Every entry is tagged along a set of axes. The axes are the wiki's lens — they decide what becomes comparable and what becomes invisible.

A wiki's `axis.json` defines its **bounded axes** (closed sets of values, displayed as filter chips) and optionally one or more **freeform axes** (open-ended slots used as prompt ingredients rather than navigation chips).

Axes make the wiki navigable as a space rather than a list. The axis set is the wiki's editorial point of view.

### Designing axes

A good axis cuts the subject in a way that produces interesting intersections. The test: does combining values across axes surface entries a curator wouldn't write unprompted? If `axis_A × axis_B × axis_C` produces obvious cells *and* genuinely strange ones, the axes are doing real work.

## The Entry — Card First, Detail Second

The card is the primary object. Every entry has:

- `title` and a 1–3 sentence `summary`
- axis values (the lens it sits under)
- a `status`: `generated` (LLM-imagined, unverified) or `explored` (human-checked, detail filled in)

An **explored** entry additionally has:

- `facts`: 3–7 label/value pairs (founded, HQ, deployment date, ...) — freeform labels, no schema
- `links`: 2–5 labeled external URLs (Wikipedia, official site, key article)
- `image`: optional, relative to the wiki's `media/`

That's the whole entry. The detail view is a small modal: facts + links + image. No prose articles by default. If an entry truly warrants a long-form treatment, a `pages/<slug>.md` file can be added later — but this is the exception, not the path.

### Entry file schema

```json
{
  "slug": "zipline",
  "title": "Zipline",
  "summary": "Autonomous medical-delivery drones operating at national scale.",
  "axes": { "energy": "electric", "scale": "individual", "range": "long" },
  "status": "explored",
  "facts": [
    { "label": "Founded", "value": "2014" },
    { "label": "First deployment", "value": "Rwanda, 2016" }
  ],
  "links": [
    { "label": "Wikipedia", "url": "https://en.wikipedia.org/wiki/Zipline_(drone_delivery_company)" },
    { "label": "Official", "url": "https://www.flyzipline.com" }
  ],
  "image": "media/zipline.jpg",
  "created": { "at": "2026-05-20", "by": "model:claude-opus-4-7" },
  "updated": { "at": "2026-05-30", "by": "user:xdze2" }
}
```

One file per entry: `wikis/<wiki>/catalogue/<slug>.json`. Git tracks history — no in-file changelog.

## Curation Over Completeness

A wiki will never be complete. The value is in the curation: cards that accurately describe how the subject actually moves through the world.

A `generated` entry is a hypothesis the LLM produced from an axis combination. An `explored` entry is one a human looked at, confirmed, and minimally annotated. Both are valid wiki content — the status tells the reader what kind of trust to extend.

## UI Layout

Three surfaces, identical across wikis:

**Top — axis bar.** One row of filter buttons per bounded axis. Multi-select within an axis; intersection across axes. Clearing an axis resets it. The axis bar is the primary navigation surface.

**Main — card grid.** Cards matching the current axis selection. Each card shows title, summary, axis chips, image thumbnail if present. `explored` cards are visually distinguished from `generated` ones (badge, border, or icon).

**Modal — entry detail.** Opens on card click. Shows facts, links, and image. Minimal. No long prose. If a `pages/<slug>.md` exists (rare), it's rendered below.

The feel is closer to a combinatorial explorer than to Wikipedia. Navigation is structural, not search-driven.

## LLM Bootstrapping

The axis grid is a generation space. For each combination of bounded-axis values, an LLM is prompted to enumerate candidate entries — a brute-force sweep across the grid surfacing cards a human curator wouldn't think to write unprompted.

The combinations are the point. Obvious cells get the obvious entries; weird cells push the LLM into genuinely obscure territory. Freeform axes (when present) add an extra prompt-time ingredient without expanding the navigation surface.

Output: one `<slug>.json` file per candidate entry, written into `wikis/<wiki>/catalogue/` with `status: "generated"`. A curation pass promotes promising ones to `explored` — adding facts, links, image, fixing the summary.

## Dev Mode vs Static Mode

The repository supports two runtimes from one codebase.

**Static mode** — `frontend/` served by any HTTP server, or an exported `dist/<wiki>/` bundle. Read-only. This is what gets deployed and shared.

**Dev mode** — `tools/dev_server.py <wiki>` runs Flask, serves the same frontend, and exposes a small JSON API: generate entries, explore (promote) an entry, edit in place, rebuild index. Localhost only, no auth. The frontend probes `/api/health` on load; if present, edit controls appear.

The exported bundle is dev mode minus the API — same files, no Flask, no edit UI.

## Repository Structure

```
frontend/                     # shared frontend (one source of truth)
  index.html
  style.css
  app.js
wikis/
  mobility_innov/
    wiki.json                 # title, wordmark, gen axes, freeform axes
    axis.json                 # axis definitions
    catalogue/
      <slug>.json             # one entry per file
    pages/                    # optional prose, rare
    media/                    # images referenced by entries
    prompts/
      make_list.txt           # per-wiki framing for generation
  data_atlas/
    ...
tools/
  build_index.py              # catalogue/*.json → wiki's index.jsonl
  dev_server.py               # Flask: frontend + wiki + edit API
  export.py                   # → dist/<wiki>/ standalone bundle
  gen_list.sh                 # invokes Claude CLI for generation
dist/                         # gitignored, generated by export.py
```

**`wiki.json`** — wiki-level metadata: title, wordmark, which axes are substituted into prompts (`gen_axes`), which are freeform ingredients (`freeform_axes`), optional `status_axis` for color-coded chips.

**`axis.json`** — bounded axes and their values. Freeform axes are not listed here (they're open-ended).

```json
{
  "axes": [
    {
      "id": "energy",
      "label": "Energy",
      "description": "...",
      "values": [
        { "id": "electric", "label": "Electric", "description": "..." },
        { "id": "human",    "label": "Human-powered", "description": "..." }
      ]
    }
  ]
}
```

**`catalogue/<slug>.json`** — one entry per file. Edited by humans and the LLM. Git-tracked.

**`index.jsonl`** — generated. Per-wiki, written by `build_index.py`. One JSON object per line, one line per entry. The frontend fetches this single file. Gitignored.

**`pages/<slug>.md`** — optional long-form prose. Rare. Loaded into the modal below facts/links when present.

## Tech Stack

Static files as the database: JSON per entry, JSON for axes and config, JSONL for the generated index, markdown for the rare prose page. Git-backed for version control and attribution.

The frontend is vanilla JS, served either by Flask (dev mode, with edit API) or any static HTTP server. No build step. No CMS. No database engine. The repository *is* the database.

Adding a new wiki is mechanical: a folder, a `wiki.json`, an `axis.json`, a prompt template. See [README.md](README.md) for the step-by-step.
