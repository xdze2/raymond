# Data Atlas — Project Vision

## What It Is

A wiki of datasets. Not a data catalog, not a repository — a reference work about data as a subject, the way Wikipedia is a reference work about the world.

Each entry is a dataset: what it is, who controls it, what it reveals, and what stands between it and public knowledge. The atlas covers both datasets that exist and datasets that should exist but don't — a gap in the record is as worth documenting as the record itself.

The closest analogies are Wikipedia (breadth, cross-linking, collaborative curation) and TVTropes (a taxonomy that becomes a lens, not just a label). The atlas is browsable the way those are — you arrive at one entry and leave through three others.

## The Axis System

Every entry is tagged along a set of axes that make datasets comparable across domains:

**Origin** — how the data came to exist:
- `sensor` — a physical measurement device
- `exhaust` — a byproduct of activity, not intentionally recorded (transaction logs, DNS queries, metadata)
- `declared` — someone chose to submit it (surveys, registries, self-reports)
- `derived` — produced by processing other datasets

**Scale** — the unit of resolution: individual, organizational, systemic, planetary

**Time frequency** — continuous, event-driven, periodic, historical, one-off

**Status** — the most important axis:
- `active` — being generated and held now
- `buried` — exists but inaccessible, controlled, suppressed
- `missing` — should exist but doesn't; the absence itself is meaningful
- `emerging` — newly possible due to technology or policy change
- `eroding` — being lost, degraded, or deleted

**LLM impact** — how AI tools change the analysis or access equation: none, low, medium, high, transformative

The axes make the atlas navigable as a space rather than a list. You can ask: what individual-scale sensor data is currently buried? What datasets are eroding before anyone archived them?

## The Status Axis Is the Point

Standard data catalogs document what exists and where to get it. This atlas also documents what doesn't exist, what's being hidden, and what's disappearing.

A "missing" entry — data that would exist if someone had chosen to collect it, or data that was never generated because no one with the means had the incentive — is a meaningful object. The absence of systematic police use-of-force data, the absence of food-additive health outcome tracking, the absence of independent audits of algorithmic sentencing tools: these are not gaps in the atlas, they are entries in it.

An "eroding" entry — data that exists now but is being lost — is equally worth documenting. Paper records before digitization, short-retention surveillance logs, discontinued sensor networks. The atlas is a record of what the world chose to measure and what it chose not to.

## What an Entry Contains

Each entry answers:
- **What it is** — the data in concrete terms: what gets recorded, how, at what resolution
- **Who controls it** — the actual chain of custody, not the nominal owner
- **What it reveals** — what can be inferred from it, at individual and population scale
- **Current access landscape** — who has it, who doesn't, how access has been gained historically
- **Cracks and pressure points** — litigation, journalism, regulation, technical circumvention, market pressure
- **LLM and AI impact** — what changes (and what doesn't) when powerful analysis tools meet access barriers
- **Relations** — links to structurally similar datasets, counterparts, complements

The format is prose, not a table. The goal is understanding, not indexing.

## Curation Over Completeness

The atlas will never be complete. That's fine — Wikipedia isn't complete either.

The value is in the curation: entries that accurately describe how data actually moves through institutions, who the real gatekeepers are, and what it would take to change that. A wrong or shallow entry is worse than no entry. The bar for inclusion is a full, accurate account of a dataset's life in the world — not just its technical specification.

This means the atlas will grow slowly and will be better for it.

## UI Layout

Three panels.

**Top — axis bar.** A horizontal filter strip, like the filter row on an e-commerce site. One row of buttons per axis: `origin`, `status`, `scale`, `time_frequency`, `llm_impact`. Clicking a value selects it (single-select per axis); the left panel updates immediately. Multiple axes can be active at once, narrowing the list by intersection. A "clear" affordance per axis resets it. The axis bar is the primary navigation surface — the way a reader orients themselves in the atlas.

**Left — entry list.** A narrow scrollable list of dataset titles matching the current axis selection. No search, no pagination — just a flat list. When no axis is selected, the full list is shown. Clicking an entry loads it in the central panel. The active entry is highlighted.

**Center — entry page.** The full content of the selected dataset entry, rendered from markdown. Title, summary, axis tags (displayed as small chips at the top), then the prose sections in order. Cross-links (`→ [[slug]]`) render as inline links that load the target entry in the same panel. The page is the destination; the left and top panels are how you get there.

The overall feel is closer to a documentation site (like Notion or Obsidian's published pages) than to Wikipedia's chrome. Navigation is structural, not search-driven.

## LLM Bootstrapping

The axis grid is also a generation space. For each combination of `origin × status × scale × domain`, an LLM can be prompted to enumerate datasets that fit those coordinates — a brute-force sweep across the space to surface entries a human curator wouldn't think to write unprompted.

The combinations are the point. `sensor × buried × planetary` is obvious (satellite data, ocean sensors). `declared × missing × individual` is more interesting — what self-reported data should exist but doesn't? `exhaust × eroding × organizational` pushes the LLM into genuinely obscure territory. The grid forces exploration of corners.

`domain` is unbounded and freeform — not a fixed taxonomy. New domains are added as needed: `medical`, `agriculture`, `finance`, `migration`, `infrastructure`. Each new domain spawns a new row of files without touching the schema. The domain slot is a prompt ingredient, not a controlled vocabulary.

The output of each LLM run is a list file — short structured entries, one per line, not yet full pages. A separate curation pass promotes promising entries to full `pages/` articles.

## Data Structure

```
data/
  axis.json
  lists/
    list_sensor_buried_individual_medical.jsonl
    list_sensor_buried_individual_law-enforcement.jsonl
    list_exhaust_active_organizational_finance.jsonl
    list_declared_missing_systemic_agriculture.jsonl
    ...
  pages/
    acoustic-gunshot-detection-shotspotter.md
    alpr-location-logs.md
    cgm-readings.md
    ...
```

**`data/axis.json`** — defines the three bounded axes and their values. The domain axis is not listed here — it is open-ended.

```json
{
  "axes": [
    {
      "id": "origin",
      "label": "Origin",
      "description": "How the data came to exist — the mechanism of its production.",
      "values": [
        { "id": "sensor",   "label": "Sensor",   "description": "Produced by a physical measurement device: cameras, microphones, accelerometers, biosensors. The world writes the data directly." },
        { "id": "exhaust",  "label": "Exhaust",  "description": "A byproduct of activity, not intentionally recorded as data. Transaction logs, metadata, DNS queries, click streams. The data exists because a system ran, not because anyone chose to capture it." },
        { "id": "declared", "label": "Declared", "description": "Someone chose to submit it. Surveys, registries, self-reports, administrative filings. The data reflects what people or institutions say, not what they do." },
        { "id": "derived",  "label": "Derived",  "description": "Produced by processing other datasets. Model outputs, aggregates, inferences, synthetic data. The data is downstream of other data." }
      ]
    },
    {
      "id": "status",
      "label": "Status",
      "description": "The current condition of the dataset — whether it is accessible, hidden, lost, or not yet real.",
      "values": [
        { "id": "active",   "label": "Active",   "color": "#2f9e44", "description": "Being generated and held now. Access may be restricted, but the data exists and is current." },
        { "id": "buried",   "label": "Buried",   "color": "#e03131", "description": "Exists but is inaccessible — controlled by a gatekeeper, suppressed, classified, or locked behind proprietary systems. The data is real; reaching it is the problem." },
        { "id": "missing",  "label": "Missing",  "color": "#f08c00", "description": "Should exist but doesn't. No one collected it, or collection was never mandated. The absence is a choice, often a political one." },
        { "id": "emerging", "label": "Emerging", "color": "#1971c2", "description": "Newly possible — a dataset that couldn't exist before due to technology, regulation, or scale, and is now beginning to be generated." },
        { "id": "eroding",  "label": "Eroding",  "color": "#868e96", "description": "Exists now but is being lost: short retention windows, discontinued sensors, decaying physical records, deliberate deletion. The window to capture it is closing." }
      ]
    },
    {
      "id": "scale",
      "label": "Scale",
      "description": "The unit of resolution — what one record in the dataset describes.",
      "values": [
        { "id": "individual",     "label": "Individual",     "description": "One record = one person, one body, one device carried by a person. The data can identify or profile a specific human being." },
        { "id": "organizational", "label": "Organizational", "description": "One record = one company, institution, vehicle, or other non-human entity. Aggregated above the person, below the population." },
        { "id": "systemic",       "label": "Systemic",       "description": "One record = a city, a market, a network, a policy domain. The data describes how a system behaves, not any single actor within it." },
        { "id": "planetary",      "label": "Planetary",      "description": "One record = a global or environmental measurement. Climate, ocean, atmosphere, species. The subject is Earth or a major system of it." }
      ]
    }
  ]
}
```

**`data/lists/list_{origin}_{status}_{scale}_{domain}.jsonl`** — one file per axis combination, generated by LLM. Each line is a candidate entry: enough to populate the list panel and decide whether to promote to a full page.

```jsonl
{"slug": "cgm-readings", "title": "Continuous Glucose Monitor Readings", "summary": "Sub-minute glucose time-series from wearable biosensors, held by Dexcom and Abbott.", "has_page": true}
{"slug": "nicu-physiological-waveforms", "title": "NICU Physiological Waveforms", "summary": "High-resolution heart rate and oxygen saturation streams from neonatal ICU monitors, rarely archived beyond discharge.", "has_page": false}
{"slug": "implanted-cardiac-device-logs", "title": "Implanted Cardiac Device Logs", "summary": "Continuous arrhythmia and pacing event logs from pacemakers and defibrillators, held by Medtronic and Abbott device platforms.", "has_page": false}
```

`has_page: true` means a full `pages/slug.md` exists. `has_page: false` means the entry is a stub — visible in the list, no page to open yet.

**`data/pages/slug.md`** — full prose entries, as described in "What an Entry Contains." Promoted manually from list stubs after curation.

The frontend loads `axis.json` once, then fetches the relevant `.jsonl` file when the user selects an axis combination. Full pages are fetched on demand by slug. No build step required to serve the site — the files are the site.

## Tech Stack

Static files as the database: markdown with frontmatter for structured fields, git-backed for version control and attribution. A minimal frontend (plain JS or Svelte) renders pages, filters via the axis bar, and navigates cross-links. No server, no CMS, no database engine — the repository is the database, the list files are the index.
