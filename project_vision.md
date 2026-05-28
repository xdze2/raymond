# Wikis — Project Vision

## What It Is

A platform for building small, focused reference works. Each wiki is a TVTropes-style atlas of a single subject: every entry sits in a multi-axis space that makes entries comparable, browsable, and generatable.

A wiki is not a catalog and not a database. It is a reference work *about* a subject, the way Wikipedia is a reference work about the world. The point is understanding through curation, cross-linking, and structural navigation — not exhaustive indexing.

The closest analogies are Wikipedia (breadth, cross-linking, collaborative curation) and TVTropes (a taxonomy that becomes a lens, not just a label). A wiki built on this platform is browsable the way those are — you arrive at one entry and leave through three others.

Current wikis in this repo:

- **`data_atlas`** — a wiki of datasets: what exists, what's buried, what's missing, what's eroding. Axes: origin, status, scale, plus open-ended domain.
- **`mobility_innov`** — a wiki of mobility innovations. Axes in progress.

New wikis are added by dropping a folder under `wikis/<name>/`.

## The Axis System

Every entry in a wiki is tagged along a set of axes. The axes are the wiki's lens — they decide what becomes comparable across entries and what becomes invisible.

A wiki's `axis.json` defines its bounded axes (closed sets of values, displayed as filter chips) and optionally one or more freeform axes (open-ended categorical slots like `domain`, used as prompt ingredients rather than navigation chips).

Axes make the wiki navigable as a space rather than a list. In `data_atlas` you can ask: *what individual-scale sensor data is currently buried?* In `mobility_innov` the analogous question is shaped by that wiki's own axes. The axis set is the wiki's editorial point of view.

### Example: data_atlas axes

- **Origin** — how the data came to exist: `sensor`, `exhaust`, `declared`, `derived`
- **Scale** — the unit of resolution: `individual`, `organizational`, `systemic`, `planetary`
- **Status** — the most important axis: `active`, `buried`, `missing`, `emerging`, `eroding`
- **Domain** (freeform) — `medical`, `agriculture`, `finance`, `migration`, ...

The `status` axis is what makes `data_atlas` different from a data catalog: it documents absence and erosion as first-class objects, not just what's accessible today.

### Designing axes for a new wiki

A good axis cuts the subject in a way that produces interesting intersections. The test: does combining values across axes surface entries a curator wouldn't write unprompted? If `axis_A × axis_B × axis_C` produces obvious cells *and* genuinely strange ones, the axes are doing real work.

## What an Entry Contains

Each entry is prose, not a table. The shape varies per wiki — `data_atlas` entries describe a dataset's chain of custody and access landscape; `mobility_innov` entries describe an innovation's mechanism and current state. What stays constant:

- A concrete description of the thing
- Who or what controls/produces/sustains it
- What it reveals, enables, or forecloses
- The current landscape — who has access, who doesn't, what's changing
- Pressure points — litigation, journalism, regulation, technology, market forces
- Relations — links to structurally similar entries, counterparts, complements

The goal is understanding, not indexing. Each wiki's `prompts/make_page.txt` encodes its own version of this shape.

## Curation Over Completeness

A wiki will never be complete. That's fine — Wikipedia isn't complete either.

The value is in the curation: entries that accurately describe how the subject actually moves through the world. A wrong or shallow entry is worse than no entry. The bar for inclusion is a full, accurate account — not just a technical specification or a name on a list.

This means each wiki will grow slowly and will be better for it.

## UI Layout

Three panels, identical across wikis (the frontend is per-wiki for deployment, but the structure is the same).

**Top — axis bar.** A horizontal filter strip, one row of buttons per bounded axis. Clicking a value selects it (single-select per axis); the left panel updates immediately. Multiple axes can be active at once, narrowing the list by intersection. A "clear" affordance per axis resets it. The axis bar is the primary navigation surface — the way a reader orients themselves in the wiki.

**Left — entry list.** A narrow scrollable list of entry titles matching the current axis selection. No search, no pagination — just a flat list. When no axis is selected, the full list is shown. Clicking an entry loads it in the central panel. The active entry is highlighted.

**Center — entry page.** The full content of the selected entry, rendered from markdown. Title, summary, axis tags (displayed as small chips at the top), then the prose sections in order. Cross-links (`→ [[slug]]`) render as inline links that load the target entry in the same panel. The page is the destination; the left and top panels are how you get there.

The overall feel is closer to a documentation site (like Notion or Obsidian's published pages) than to Wikipedia's chrome. Navigation is structural, not search-driven.

## LLM Bootstrapping

The axis grid is also a generation space. For each combination of bounded-axis values (and optionally a freeform-axis ingredient like `domain`), an LLM is prompted to enumerate entries that fit those coordinates — a brute-force sweep across the space to surface entries a human curator wouldn't think to write unprompted.

The combinations are the point. In `data_atlas`, `sensor × buried × planetary` is obvious (satellite data, ocean sensors); `declared × missing × individual` is more interesting — what self-reported data should exist but doesn't? `exhaust × eroding × organizational` pushes the LLM into genuinely obscure territory. The grid forces exploration of corners. Each wiki has its own equivalent corners.

Freeform axes (like `domain`) are unbounded — not a fixed taxonomy. New values are added as needed and each new value spawns a new row of files without touching the schema. Freeform slots are prompt ingredients, not controlled vocabularies.

The output of each LLM run is a JSONL file written to `wikis/<wiki>/catalogue/`. Each line is a candidate entry with axis values embedded, enough to appear in the list panel and be filtered immediately. A separate curation pass promotes promising entries to full `pages/` articles. Adding a new catalogue file requires only dropping the file and adding its name to `catalogue/index.json` (via `update_index.sh`).

## Repository Structure

```
wikis/
  data_atlas/
    wiki.json          # title, wordmark, axes used by gen_list.sh, extra chips
    axis.json          # axis definitions (id, label, values)
    catalogue/
      index.json
      list_sensor_buried_individual_medical.jsonl
      ...
    pages/
      index.json
      acoustic-gunshot-detection-shotspotter.md
      ...
    prompts/
      make_list.txt    # per-wiki framing for catalogue generation
      make_page.txt    # per-wiki framing for full-page promotion
    frontend/
      index.html
      style.css
  mobility_innov/
    ...
gen_list.sh            # generate a catalogue file via Claude CLI
update_index.sh        # rebuild catalogue/index.json after adding files
```

**`wikis/<wiki>/wiki.json`** — wiki-level metadata: title, wordmark, which axes are substituted into prompts (`gen_axes`), which are freeform ingredients (`freeform_axes`), optional `status_axis` for color-coded chips, and `extra_chips` for display.

**`wikis/<wiki>/axis.json`** — defines the wiki's bounded axes and their values. Freeform axes are not listed here — they are open-ended.

```json
{
  "axes": [
    {
      "id": "origin",
      "label": "Origin",
      "description": "How the data came to exist — the mechanism of its production.",
      "values": [
        { "id": "sensor",   "label": "Sensor",   "description": "Produced by a physical measurement device." },
        { "id": "exhaust",  "label": "Exhaust",  "description": "A byproduct of activity, not intentionally recorded as data." },
        { "id": "declared", "label": "Declared", "description": "Someone chose to submit it." },
        { "id": "derived",  "label": "Derived",  "description": "Produced by processing other datasets." }
      ]
    }
    // ... more axes
  ]
}
```

**`wikis/<wiki>/catalogue/`** — the flat entry catalogue, split across multiple JSONL files. Each file is one LLM generation run. The filename is for human orientation only; the frontend does not parse it. `catalogue/index.json` lists all filenames to load.

Each line is a catalogue entry carrying its axis values directly:

```jsonl
{"slug": "nicu-physiological-waveforms", "title": "NICU Physiological Waveforms", "summary": "High-resolution heart rate and oxygen saturation streams from neonatal ICU monitors, rarely archived beyond discharge.", "origin": "sensor", "status": "buried", "scale": "individual", "has_page": false}
```

The catalogue is the authoritative entry list. Deduplication is by `slug` — if a slug appears in multiple files, the first occurrence wins. A full page entry always overrides a catalogue stub.

**`wikis/<wiki>/pages/index.json`** — a flat array of slugs that have a full prose page. The frontend cross-references this against the catalogue to attach `page_url` to matching entries. No per-entry HTTP probing needed.

**`wikis/<wiki>/pages/<slug>.md`** — full prose entries. Promoted manually from catalogue stubs after curation.

The frontend loads `wiki.json`, `axis.json`, and both index files once, then fetches all catalogue JSONL files in parallel. Filtering happens client-side against the merged entry map. Full page markdown is fetched on demand when an entry is clicked. No build step required — the files are the site.

## Tech Stack

Static files as the database: markdown for prose entries, JSON for axes and indexes, JSONL for catalogue rows. Git-backed for version control and attribution. A minimal vanilla-JS frontend per wiki renders pages, filters via the axis bar, and navigates cross-links. No server, no CMS, no database engine — the repository is the database, the list files are the index.

Generation is driven by `gen_list.sh`, which reads `wiki.json` to know which axes to substitute into `prompts/make_list.txt`, invokes the Claude CLI, and writes JSONL into the wiki's catalogue. `update_index.sh` rebuilds `catalogue/index.json` so the frontend picks up new files.

Adding a new wiki is mechanical: a folder, a `wiki.json`, an `axis.json`, a prompt template, and a copy of the frontend. See [README.md](README.md) for the step-by-step.
