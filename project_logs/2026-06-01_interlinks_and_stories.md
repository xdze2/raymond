# Interlinks, stories, and the human bottleneck

Brainstorm session, 2026-06-01. Captures ideas around three connected
questions: how to link entries to each other, how to surface "stories"
through the atlas, and how to handle information overload without falling
into the gamification trap.

## The Queneau north star

The project is named Raymond, after Raymond Queneau, and that lineage
should be the design compass — not generic gamification, not
screenwriting tropes, not knowledge-graph orthodoxy.

Two Queneau works are directly relevant:

- ***Cent mille milliards de poèmes*** (1961) — ten sonnets cut into
  strips so any line can be swapped with any other. 10^14 readable
  poems from 140 lines. **Combinatorial storytelling with a fixed
  substrate.** Our atlas is the substrate (cards + edges); the story
  generator is the cutting and recombining.
- ***Exercices de style*** (1947) — the same banal incident retold 99
  different ways. **The story is not in the facts; it is in the
  framing, the constraint, the voice.** A given path through the atlas
  isn't one story — it's the seed for many, depending on which
  rhetorical lens the narrator wears.

The Oulipo principle: **constraint is generative, not limiting.** This
is the opposite of "more cards, more axes, more features." Subtractive
design with strong rules produces more interesting output than
permissive design with weak ones. Every design choice below should be
read in that light.

## The framing

- Axes are the **space** — the field to explore.
- Stories are the **paths** through that space — tension, progression,
  contradiction, reframing.
- The bottleneck is the user's brain, not the catalogue's size. Goal:
  make exploration fun and easy, not exhaustive.
- Information overload is a *design* problem before it's a motivation
  problem. Subtractive design (smaller slices, guided paths) beats
  additive design (XP, streaks, badges) for a curated atlas.

## Why not gamification

External rewards (points, levels, completion %) train the user to
optimize the meter instead of the content. For a personal-curation
project the appeal is partly that it *isn't* a game. The one defensible
"gamey" mechanic is lightweight active recall ("which came first?"),
framed as curiosity not testing — no scores, no streaks.

What to do instead:

- **Lens of the day**: pick one axis value, show only those entries,
  one-line framing question at top. Turns 100 cards into ~8 with a
  thread.
- **Trails**: walk 4–6 connected entries in sequence, one screen each.
  Needs interlinks to exist.
- **"What's new"**: honest novelty (5 new entries this week) as a
  return hook, not a fabricated daily streak.

## Interlinks — the load-bearing piece

When browsing cards the natural question is *"what is the story here?"*
Stories need edges to walk on. Without interlinks, paths are random
axis-space samples; with them, they're actual semantic traversals.
Edges-first is the right order.

### Design decisions to lock in early

1. **Verb vocabulary — hybrid.** Closed enum of relation *categories*
   declared in `wiki.json` (`lineage`, `succession`, `implements`,
   `rivalry`, `affiliation`, `cites`, …) plus a free-text `phrase` for
   the human-readable label. LLM picks one category + writes the
   phrase. Enum keeps filtering/coloring tractable; phrase keeps it
   readable.
2. **Directed.** "Mead → advised → Mahowald" ≠ the reverse. Cheap now,
   painful to retrofit. Frontend can render both directions, but the
   data knows which way the arrow points.
3. **Single source of truth, inverse computed at index time.** Edges
   live on the source entry as
   `related: [{slug, category, phrase}]`. `build_index.py` walks all
   entries, applies declared inverses from `wiki.json`
   (`advised ↔ advised_by`), and attaches inbound edges to each
   entry's index record. No drift between sides.
4. **Grounding rule.** An edge is a factual claim. The LLM can only
   assert one if it's supported by `seed.enrichment` or
   `seed.ddg_search`. Otherwise it connects things by vibes — and
   stories built on hallucinated edges sound right but are wrong.
5. **Density target.** ~3–5 outbound edges per entry. Too few →
   dead-end walks; too many → no signal. Prompt caps it.

### Write paths (eventually all three)

- **At explore time** — natural moment, full context. Add to
  `make_page.txt`, validate slugs in `explore.py`.
- **Re-link pass** (`tools/link_entries.py`) — edges added in March
  can't reference entries added in May. Maintenance op.
- **By hand** — edit-mode UI for adding/removing edges. Some
  connections you just know.

### Suggested build order

1. Declare edge categories + inverses in `wiki.json`.
2. Update `make_page.txt`: ask for `related[]` with category + phrase +
   target slug; ground in sources; validate in `explore.py`.
3. Re-run `explore` over the ~50 existing neuromorphic entries with
   Mistral (cheap) — get a real graph to look at.
4. Compute inbound edges in `build_index.py`.
5. Render in modal: "connections" section grouped by category, each
   chip is a click-through with the phrase as label.
6. *Then* look at the resulting graph and decide whether re-link pass
   or manual editor is more urgent. Don't build either speculatively.

Step 3 is the moment of truth — that's when you find out whether the
LLM picks good connections or whether the prompt/sources need work.

## Storytelling — the longer-term bet

Once edges exist, the atlas becomes walkable. The story generator is
the thing that makes it *re-readable* — same 100 cards, different
story every visit. That's the real answer to information overload:
not less information, but a renewable way to encounter it.

### What makes a path a story (not a list)

- **Through-line** — each step connected to the last by some relation.
- **Delta** — something changes across the path (time, scale, framing,
  discipline).
- **Tension** — somewhere mid-path, an obvious step *isn't* taken, or
  two entries contradict. This is where LLMs add real value.
- **Closure** — the last card recontextualizes the first.

### Two-tier generation

Permutations of N cards is N! — useless. Instead:

1. **Generate cheaply (combinatorial, no LLM):** constrained random
   walks of length 4–7 on the related-edges graph. Weight by
   edge-verb diversity (penalize three "successor" hops in a row).
   Bias starting nodes toward anchors (people, foundational concepts).
   Score axis-crossing higher than axis-staying. A handful of
   structural templates as seeds: *origin → branch → branch →
   reunion*, *thesis → antithesis → synthesis*, *teacher → student →
   student's student*, *problem → attempt → failure → next attempt*.
   Produce 50–200 candidates.

2. **Rank cheaply with the LLM as a critic, not a writer.** One
   batched call, score each path 1–5 on: through-line, tension, span,
   closure; plus a 15-word "what is this story about" pitch (which
   becomes the title). Keep top 5.

3. **Narrate only the winners.** Bigger LLM call writes the actual
   200-word narrative for the top picks. Strict grounding: narrator
   uses only facts present in `facts[]` and `summary` of the entries
   in the path — any new date/name is a bug.

### UI shape

`/stories` view. "Find me a story" button → backend runs the
generate/rank/narrate pipeline → shows top 3 as cards (title, pitch,
visual chain of cards). Click one → full narrative with each card
inline. User ↑/↓ vote → eval signal for tuning the scorer. Over time
the system learns which templates and axis-crossings produce stories
*this* user likes — that's a flywheel, not gamification.

### The risk

LLM narrators drift into plausible-sounding nonsense, especially with
tension/contradiction prompts (model will *invent* contradictions to
satisfy the rubric). Same grounding discipline as explore. The edges
being well-grounded (the interlinks step above) is what makes this
viable downstream.

## Narrative craft — what the literature actually offers

Storytelling is a well-studied domain. Most of it doesn't transfer to a
4–7 card walk through a curated atlas — a knowledge path has no
protagonist arc, no dialogue, no scenes. But a few principles survive
the translation, and they sharpen both the ranker and the narrator.

### Frameworks worth borrowing

- ***Kishōtenketsu*** (Japanese four-act: introduction → development →
  **twist** → reconciliation). No conflict required — just a turn that
  recontextualizes what came before. Fits a knowledge atlas perfectly.
  Many neuromorphic stories aren't about conflict, they're about a
  reframing ("everyone was scaling digital → Mead said use physics →
  analog VLSI → today's mixed-signal chips"). Use as a default
  structural template in the walk generator.
- **Story circle / *anagnorisis*** (Aristotle's recognition). The last
  card should make you re-read the first card differently. This is the
  *closure* rubric item — worth weighting heavily.
- **Forster's causality**: *"The king died and then the queen died"* is
  a sequence; *"The king died and then the queen died of grief"* is a
  story. **The edge verb is doing the story-making work** —
  `succession` is sequence, `refutes` / `enables` / `rendered obsolete`
  are causal. Down-weight chronological edges in walk generation;
  up-weight causal ones.
- **Hitchcock's suspense vs. surprise.** Suspense (reader knows
  something is coming) is easier to engineer than surprise (sudden
  reveal). Narrator instruction: *card 1's prose hints at card N's
  destination, without naming it.*
- **Chekhov's gun.** A detail in card 1's narration should pay off in
  the final card. Testable in the ranker.

### Frameworks to skip

- **Hero's journey / monomyth.** Too many beats for a 5-card path;
  no protagonist arc; cargo-cult risk.
- **Freytag's pyramid.** Too coarse at this length.
- **Multiple POVs / unreliable narration / nonlinear time.** Tempting
  but expensive to do well. The atlas already has nonlinearity (the
  user clicks around); the narrator's job is to impose order, not
  subvert it.

### What recent work on LLM micro-stories actually shows

- **Setup → expectation → violation → resolution** is the structural
  pattern human raters reliably prefer. This is *kishōtenketsu* by
  another name — and it's been validated empirically.
- **LLMs over-resolve.** Left alone they wrap every story with a bow.
  Forcing the narrator to leave a thread *open* ("we still don't know
  whether spike-based learning will scale") makes the output land
  harder. Instruction: *end with a question, not a conclusion.*
- **Specificity beats generality.** "In 1989" beats "in the late 1980s";
  "ten million synapses" beats "many synapses". LLMs default to
  abstraction. Instruction: *use the specific numbers and dates from
  `facts[]`; never round, never generalize.*
- **Tension comes from constraint, not violence.** Surface what was
  hard or counterintuitive at the time of each entry.

### The Queneau move: voice as constraint (Exercices de style)

The narrator is not a single voice. *Exercices de style* tells us a
story is also defined by **how** it is told. Once the base narrator
works, the same path should be re-tellable through different
rhetorical lenses — each a separate, declared constraint:

- **Chronicle** — sober, dated, encyclopedic.
- **Detective** — start at the end, work backward to the cause.
- **Letter from the era** — first-person, present tense, from inside
  the field at the time of card N.
- **Obituary** — for a person-anchored path, frame as a life-shaped arc.
- **Manifesto** — polemical, taking the side of one of the entries.
- **Footnote** — pretend the whole story is a digression from
  something else.

This is *not* a "fun extra" — it's the Oulipo principle applied. Each
lens is a constraint that re-shapes the same combinatorial substrate
into a different readable text. *Cent mille milliards de poèmes* with
a knob for voice.

### Refined ranker rubric

Replacing the original 4-axis sketch:

| Axis | What to look for |
|---|---|
| **Setup → violation** | Does card 4 or 5 contradict an expectation set up in card 1? (kishōtenketsu / anagnorisis) |
| **Causal density** | What fraction of edges on the path are causal verbs vs. chronological? (Forster) |
| **Protagonist presence** | At least one person entry in the path? (cheap heuristic — people are protagonists, chips aren't) |
| **Closure with opening** | Does the last card re-illuminate the first? (story circle) |
| **Specificity** | Density of dates / numbers / named entities in the path's `facts[]` — computable without an LLM, use as pre-filter |

### Narrator-prompt spine (six instructions)

1. **Structure**: kishōtenketsu (intro / develop / twist / reconcile),
   adapted to path length.
2. **Hook**: open card 1 with a question or tension; do not name the
   destination.
3. **Causality**: use the edge verbs explicitly — "X, which Y rendered
   obsolete…", not "X. Then Y."
4. **Specificity**: every claim grounded in `facts[]`; no rounded
   dates; named people, not "researchers."
5. **Chekhov**: plant one detail in card 1's prose that recurs in the
   final card.
6. **End open**: last sentence is a question or unresolved tension, not
   a wrap-up.

Plus a seventh, when voice-lenses ship: **constraint** — the chosen
rhetorical mode (chronicle, detective, letter, …) is declared and
binding for the whole narration.

### One-line synthesis

**The edge verbs are doing more work than the cards.** A path is
interesting because of the *relations* between cards, not the cards
themselves. The edge vocabulary (hybrid category + free-text phrase)
isn't metadata — it's the grammar of every story the atlas will ever
tell. Choose it like Queneau chose his sonnet form: tightly, on
purpose, knowing every later combinatorial move depends on it.

## Dependency chain

```
edges (G in todo.md)
  ↓
inbound-edge computation in build_index
  ↓
connections section in modal  ← shippable here, real value
  ↓
walk generator (combinatorial)
  ↓
story ranker (LLM-as-critic)
  ↓
narrator + /stories UI
```

Every step before the story generator is independently valuable. The
story feature is the payoff, but even if it never ships the wiki is
dramatically better with edges in place.
