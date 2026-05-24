You are building an "Data Atlas" — a structured wiki cataloguing every
significant type of data that exists (or could be) in the world: how it comes into
being, who controls it, what it reveals, and how its accessibility
is changing.

Your task is to generate seed lists of real, or possible, specific data types —
not abstract categories, but concrete phenomena that deserve their
own page.

Rules:

- Be specific. Not "medical data" but "post-surgical complication rates
  by hospital and surgeon"
- Name real systems, institutions, or technologies where relevant
- Include both well-known and obscure examples
- Include data that is currently inaccessible, suppressed, or not yet
  collected — mark these with [MISSING]
- Include data that is technically available but practically inaccessible
  — mark these with [BURIED]
- Do not repeat across lists — each item belongs to exactly one list
- Aim for genuine variety across domains: medical, financial, legal,
  environmental, social, political, scientific, behavioral

---

Generate the following four lists:

## LIST 1: SENSORS & CAPTURED DATA

Data produced by instruments pointed at the world.
The world as author. No human intended to produce this —
a device recorded what was there.
Include: physical sensors, biological sensors, remote sensing,
passive surveillance, environmental monitoring.
~50 items.

Examples of the right level of specificity:

- Continuous glucose monitor readings (CGM)
- Seismic sensor arrays around nuclear test sites
- Automated license plate reader (ALPR) location logs
- Satellite synthetic aperture radar (SAR) imagery of industrial sites

## LIST 2: EXHAUST & TRACE DATA

Data produced as a byproduct of doing something else.
The activity as author. Nobody created this to be informative —
it accumulated as residue of action.
Include: behavioral logs, transaction records, communication metadata,
operational logs, digital footprints.
~50 items.

Examples of the right level of specificity:

- Cell tower connection logs by carrier
- Supermarket loyalty card purchase sequences
- DNS query logs at ISP level
- Elevator usage patterns in office buildings

---

For each item use this compact format:

[NAME] — [one sentence: what it is, who produces it, who controls it]
Tags: scale=[individual/organizational/systemic]
domain=[domain(s)]
status=[active/buried/missing/emerging]

---

Create one markdown file per list, in data_lists.
After each list, add a short paragraph:
PATTERN NOTE — what distinguishes this origin type,
what power dynamics are typical,
where LLMs are most likely to change access.
