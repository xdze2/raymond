# The question graph — a second floor on the atlas

Brainstorm session, 2026-06-01 (follow-up to `2026-06-01_interlinks_and_stories.md`).
Captures a shift in framing that may pivot the project: from "atlas of
cards you browse" to "atlas of cards plus a graph of arguments built
on top." The card layer stays; a second layer is added.

## The trigger

Two pieces collided in the same session and changed the picture.

**First**, an Instagram post about pedagogy:

> The design question is not just *"how do I explain this clearly?"*
> It's *"how do I make the learner need the explanation before it
> arrives?"*

**Second**, trying to write down a real question I have about
neuromorphic computing:

> There is a very strong energy wall on current AI development, but
> this is purely due to historical reasons — computers and their
> fabrication processes are not "LLM-native." The proof is biological
> brain power usage. Now that there is huge domain and market
> pressure, a second AI revolution is going to happen. The question is
> where and when?

That sentence does in two breaths what the current atlas can't do at
all. It sets up a **wall**, then a **reframe**, then **evidence**, then
**stakes**, then an **open question**. The structure is not
encyclopedic — it is rhetorical. And no card-based atlas, ours or
anyone else's, is built to answer a question shaped like that.

## The shift in framing

Current framing: the atlas is a **well-structured answer space.**
Cards are answers waiting to be encountered. The reader brings their
own question. The LLM fills, links, narrates.

New framing: the atlas is a **question generator** stacked on top of
the answer space. Cards are still the substrate. But the product —
the thing the reader actually consumes — is **a reading path that
manufactures the need for each card just before the card arrives.**

This inverts the convention. Wikipedia hands you the answer and trusts
you brought the question. Search returns documents and trusts you can
extract what you needed. The new framing **hands you a question
first**, then the answer — and the question is what makes the answer
stick.

The pedagogical name for this is the *testing effect* / Socratic setup.
The Oulipo name is the constraint that makes the substrate productive.
The mechanical name is **two graphs, two natures.**

## Two graphs, two natures

The critical insight: there are two graphs in play, and they are
genuinely different kinds of things. Conflating them is the mistake
every knowledge-graph project makes. Keeping them separate is the
move.

### Card graph (already exists, mostly)

- **Nodes are things that exist in the world** — people, chips, labs,
  concepts, papers. Entries in `catalogue/<slug>.json`.
- **Edges are factual relations** — "advised," "succeeded,"
  "implements," "rivals." Designed in the previous log
  (`2026-06-01_interlinks_and_stories.md`).
- **Discovered.** Facts ground it. The LLM can hallucinate but it can't
  invent Carver Mead. Verifiable. Stable across readers.

### Question graph (new)

- **Nodes are moves in an argument** — a wall, a reframe, a piece of
  evidence, a stake, an open question, an analogy, a counter-example.
- **Edges are rhetorical relations** — "this reframes that," "this is
  evidence for that," "this creates the question that," "this raises
  the stakes of that."
- **Constructed.** There is no fact of the matter about whether
  something is a "wall" or a "reframe." It depends on the reader's
  prior, the moment in the argument, the framing.

### How they relate

```
Question graph  ── grounded_by ──►  Card graph
   (rhetorical,                       (factual,
    constructed)                       discovered)
```

A question-graph node *points at* card-graph nodes as its evidence.
"The energy wall" (question node) is grounded by cards like
[datacenter-power-consumption], [gpu-tdp-trends],
[training-cost-gpt4]. "Brains do this differently" (question node) is
grounded by [biological-neuron-energy], [sparse-coding],
[event-driven-sensing].

A reading path is a **walk through the question graph**, where each
node renders by pulling in its grounding cards. The card graph is the
substrate; the question graph is the score.

This is *Cent mille milliards de poèmes* exactly, but cleaner than the
previous log managed to state it. **Cards are the sonnet lines, fixed.
Question graphs are the readings.** There isn't one question graph —
there are many, one per question someone arrives with. 140 lines;
10^14 readings.

## Why this is bigger than it looks

Three consequences worth sitting with.

### The grounding rule becomes sharper, not blurrier

The previous log's grounding rule: "an edge is a factual claim, must
be supported by sources." Under the two-graph model that splits in
two, and both rules are tighter:

- A **card-graph edge** ("Mead advised Mahowald") must be grounded in
  external sources (`seed.enrichment`, `seed.ddg_search`).
- A **question-graph node** ("the energy wall is historical, not
  physical") must be grounded in **cards** — at least one, usually
  several. A question node with no `grounded_by` is bullshit and
  refused.

That second rule is what keeps the argument layer from becoming pure
LLM confabulation. The model can be creative about *which* moves to
make, but every move has to stand on cards that exist. Same Queneau
discipline as before, applied one level up.

### Question nodes are reusable across paths

"The energy wall" is a wall that appears in many reading paths — not
just the neuromorphic one. It's also in arguments about edge
computing, climate impact of AI, the limits of scaling laws. The same
node, the same grounding cards, slotted into different argument
structures. **The question graph is itself a catalogue — of moves,
not entities.**

This is what makes the second floor worth building. A library of
rhetorical primitives accumulates: a wall, a reframe, an
analogy-to-biology, an evidence-from-history, a market-pressure-stake,
an open-empirical-question. These compose. They have *types*. And the
types match the storytelling vocabulary the previous log already
imported:

- *kishōtenketsu* → setup / development / **twist** (a question-graph
  node typed "reframe") / reconciliation
- Forster's causality → edges typed "creates_question" or
  "answered_by" rather than chronological
- *anagnorisis* → the closing question-graph node re-illuminates the
  opening one
- Hitchcock's suspense → setup nodes that hint without naming
- Chekhov's gun → a fact introduced in an early node pays off in a
  later one

The literature pulled in last time wasn't decoration. **It's the type
system for question-graph nodes.** That retroactively explains why
those frameworks felt right and the hero's-journey/Freytag ones didn't:
the surviving ones describe rhetorical *moves*, which is what
question-graph nodes are.

### Two activities, two surfaces

Curating cards is what's been built so far: read a source, write down
what's true, tag it, link it. Librarian work.

Curating question nodes is a different activity. **It's closer to
drafting essays.** You're not recording facts; you're recording moves.
The user who curates question nodes is doing the work of a theorist,
not a cataloger.

These probably want separate surfaces. The card surface stays as it is
(the current frontend). The question-graph surface is a new thing,
maybe a new view, maybe a separate tool. Question nodes feel more like
**drafts of arguments** than like wiki entries — they might want to
live in `arguments/` next to `catalogue/`, with their own schema and
their own editor.

## Schema sketch

Just to make it concrete — not committing to the field names yet.

```json
// catalogue/<slug>.json — unchanged
{
  "slug": "carver-mead",
  "title": "Carver Mead",
  "facts": [...],
  "axes": {...},
  "related": [...]
}

// arguments/<slug>.json — new
{
  "slug": "energy-wall-is-historical",
  "type": "reframe",
  "claim": "The energy gap between brains and silicon is an artifact of how we built computers, not a physical limit.",
  "grounded_by": ["datacenter-power-consumption", "biological-neuron-energy", "von-neumann-bottleneck"],
  "creates_question": "If it's historical, what would the non-historical alternative look like?",
  "answered_by": ["analog-vlsi", "in-memory-compute", "neuromorphic-chips"]
}
```

Two kinds of outbound edges from an argument node:

- `grounded_by` — points **down** into cards (factual substrate).
- `creates_question` / `answered_by` / `reframes` / `raises_stakes_of`
  — points **across** to other argument nodes (rhetorical structure).

A reading path is a sequence of argument-node slugs. Rendering pulls
in the grounding cards for each. That's the whole machine.

The `type` enum needs design. First-cut candidates, derived from the
neuromorphic example: `wall`, `reframe`, `evidence`, `stakes`,
`open_question`, `analogy`, `counter_example`, `historical_accident`,
`failure_mode`, `prediction`. Keep it small at first; expand only when
a real path demands a missing type. Same Queneau discipline as the
edge-verb vocabulary in the previous log — **the type system is the
grammar of every argument the atlas will ever stage.**

## The pipeline (and why it's the same machine as the story generator)

For an input question from the user:

1. **Decompose.** LLM splits the question into 5–8 sub-questions whose
   answers, in order, would constitute an answer to the whole.
2. **Match / propose.** For each sub-question, either match an
   existing argument node (reusable library) or propose a new one,
   typed and grounded in cards from the catalogue. Flag
   `MISSING_CARD` if the grounding doesn't exist.
3. **Order.** Sequence the nodes so each answer creates the next
   question. Apply structural templates (kishōtenketsu by default).
4. **Render.** For each node, pull grounding cards; write the setup
   line that frames *why this card matters now*.

This is the **same machine** as the story generator from the previous
log. The story generator picks the question itself (using generic
structural templates: *what gets reframed?*, *what tension is left
open?*). The question-driven version takes the question as input from
a reader. Same pipeline, different prompt at step 1. **They unify.**

This is a real simplification. The previous log had "story generator"
and "narrator" as one stack and "agents that find tensions / missing
edges" as a parallel stack. Under the two-graph model, both stacks
are producing **question-graph fragments** — one driven by structural
templates, one driven by reader questions, one driven by automated
curation passes. The output schema is the same. The consumer (the
reading-path renderer) is the same.

## What this means for the existing roadmap

The previous log laid out a dependency chain:

```
edges → inbound computation → connections in modal
  → verify_facts.py (parallel)
  → walk generator → ranker → narrator → /stories → voice-lenses
  → find_tensions feeds the ranker
```

That chain isn't wrong, but it's now seen through a different lens.
Every step before the narrator was building the **card graph**.
Everything from the walk generator on is the **question graph** —
just unnamed and conflated with cards.

Re-reading the chain under the new model:

- **Edges (card-graph layer)** — still load-bearing, still the right
  next step. Build them.
- **`verify_facts.py`** — purely card-graph hygiene. Build it after
  edges as planned. Unaffected.
- **Walk generator → ranker → narrator** — this is the question graph,
  but built **transiently** (each walk discards its argument
  structure). The pivot says: don't discard it. **Persist the
  argument fragments** the ranker liked. Over time the argument graph
  *accretes* from the story-generation pipeline. The atlas gets
  smarter at telling stories the more stories it's told.
- **`find_tensions.py`** — produces question-graph nodes typed
  `tension` / `counter_example`. Already designed correctly; the
  pivot just names what it was always doing.
- **Voice lenses (Exercices de style)** — operate on the question
  graph, not the card graph. Same path, different rhetorical render.
  The voice-lens machinery is unchanged; it just has a more honest
  name for its input now.

So the pivot doesn't throw work out. It **reinterprets the back half
of the chain** as construction of a persistent second graph, and adds
one new capability on top: **reader-driven question paths**, where
the input isn't a structural template but a real question someone
typed.

## The deeper claim about LLMs

This is where the underlying quest — *how do LLMs change the way we
work with information?* — gets a sharper answer than any of the
earlier brainstorms produced.

Search built flat retrieval. Wikipedia built a card graph by hand over
twenty years. Nobody has built a public, reusable **argument graph**,
because the labor is enormous and the verification is hard — you need
both factual grounding *and* rhetorical judgment, at scale.

**LLMs are uniquely good at the argument layer.** They can propose
argument-graph nodes from a card graph faster than any human, and the
human can review and approve. They can also *consume* the argument
graph to produce reading paths tailored to a real reader's real
question. That capability didn't exist before 2023.

The bet: LLMs don't primarily change retrieval (search was already
good). They change **construction of argument structures over factual
substrates**. The atlas is the simplest possible testbed for that
bet — small enough to verify, large enough to be interesting, with a
clean separation between the factual layer (cards) and the argument
layer (question graph) so we can tell which one the LLM is helping
with and how much.

## The prototype

Don't design the schema yet. Build the smallest thing that proves the
two-graph idea is real.

**Script** (one afternoon, ~80 lines):

```
input:  a question (the neuromorphic one, verbatim)
input:  the catalogue of ~50 cards (summaries + facts)

LLM call 1: decompose the question into 5-8 sub-questions
LLM call 2: for each sub-question, propose an argument node:
              type, claim, grounded_by (card slugs from catalogue),
              or MISSING_CARD: <description>
LLM call 3: order the nodes; for each, write a one-line setup
            that frames why the next card matters now

output: the reading path as a markdown file +
        a graphviz diagram of the question-graph fragment with
        grounding-card edges drawn into the card layer below
```

Run it on three questions:

1. The neuromorphic one (well-covered domain — does it cohere?).
2. A question the catalogue **shouldn't** be able to answer ("how does
   neuromorphic relate to optical computing?") — observe the
   `MISSING_CARD` rate. Failure mode is informative.
3. A question that's adjacent but tilted ("why hasn't neuromorphic
   won yet, given the obvious advantages?") — does the pipeline pick
   a *different* set of cards in a *different* order from #1, or does
   it converge to the same path? Independence test.

What we learn from the three outputs, in one afternoon:

- **Does the existing catalogue cover the question I actually care
  about?** If half the answers are `MISSING_CARD`, curation has been
  driven by what was stumbled into, not by what would answer real
  questions. That alone reshapes how to curate next.
- **Does the LLM's decomposition match mine?** If it picks the same
  sub-questions, it can do this work. If it picks *better* ones,
  that's the moment of truth for the whole project.
- **Is the ordering interesting?** A bad ordering is a list. A good
  ordering is a path where each card recontextualizes the previous.
  The difference is felt immediately.
- **Does the graphviz diagram look like an argument or like a list
  with arrows?** That's the test of whether the second graph is real
  or imagined.

If even one of the three reading paths feels like something you'd
want to read end-to-end, the pivot is real. If none do, the pivot is
premature and the existing edges-first plan stands.

## What's intentionally left undecided

- **Whether question nodes are per-wiki or cross-wiki.** Reusability
  argues for cross-wiki (a `wall` is a `wall` whether the substrate
  is neuromorphic or mobility). Coherence argues for per-wiki (each
  wiki has its own editorial voice). Defer until the prototype runs.
- **Whether readers can save / share their question-graph fragments.**
  Possibly the most interesting product surface — *"here's how I came
  to understand neuromorphic computing, walk it yourself"* — but
  pure speculation until the prototype answers whether the fragments
  are worth saving.
- **The argument-node type enum.** Sketched above; will be wrong on
  first contact. Design it after the prototype produces 30 nodes by
  hand and the natural categories emerge.
- **The editor surface for argument nodes.** They're not wiki entries;
  they probably don't belong in the existing modal. New view, new
  tool, or just text files for now — decide after the prototype.

## One-line synthesis

**The card atlas tells you what exists. The question graph tells you
why you should care, in what order, and what to ask next.** They are
different kinds of objects, built differently, verified differently,
and consumed differently — and stacking them is what an LLM-native
reference work actually looks like.

---

## Postscript — what if we started from chat instead?

Later in the same session, a harder question came up: **forget the
current project state. If we started from scratch, what would the
right interface be?**

Chatting with an LLM is actually a very good interface — easy,
rewarding, zero friction to start. But it has known failure modes
that the project has been trying to design around without naming:

- **No persistence of structure.** The conversation is a transcript,
  not a map. Yesterday's insight is buried in scrollback.
- **No branching.** Every *"wait, what about X?"* either abandons the
  current thread or forks unrecorded.
- **No accumulation across sessions.** Tomorrow you start cold.
- **No external view.** You can't *see* what you've explored.

The card atlas was an attempt to fix all four at once by **front-loading
curation**. The redesign considered here flips the order: **let chat
stay the interaction, and harvest the structure as a byproduct.**

### The interface idea

A single screen, split:

```
┌─────────────────────────────────┬──────────────────────┐
│                                 │                      │
│      CONVERSATION (live)        │     MAP (persistent) │
│                                 │                      │
│  You: what about neuromorphic?  │   ● your question    │
│  AI:  [answer with citations]   │   ├─ ● energy wall   │
│       Want to go deeper on:     │   │  └─ ● brains     │
│       [energy] [history] [chip] │   ├─ ○ history       │
│                                 │   └─ ○ chips         │
│  You: energy →                  │                      │
│  ...                            │   (● visited         │
│                                 │    ○ suggested)      │
└─────────────────────────────────┴──────────────────────┘
```

Left: a normal chat. Right: **the conversation, externalized as a
tree, in real time.** Every answer plants 2–4 suggested branches as
ghost nodes. Clicking a ghost continues the chat in that direction.
Backing up doesn't abandon a thread — it's still on the map, ready
to revisit. Dangling directions are visible, not lost.

This is the answer to "chat doesn't build a knowledge base":
**the chat is the interaction, the map is the accumulation.** Same
session produces both, no extra effort.

### Why this isn't just "ChatGPT with a sidebar"

ChatGPT has a sidebar of past conversations. That's a filing cabinet,
not a map. The missing thing is **spatial structure within a single
exploration:**

- You can see the *shape* of what you've explored — wide and shallow
  vs. narrow and deep.
- Going back is cheap. Click a previous node, branch again, the old
  path is still there.
- Accumulation is automatic. The map is the artifact. You don't curate
  it; it grows as you chat.

### Three layers of persistence

Decreasing in volume, increasing in curation:

1. **Conversation log.** Raw transcript. Every message, every branch,
   every ghost node. Append-only. Audit trail.
2. **Exploration map.** Computed from layer 1. Nodes are *questions
   or topics* (not individual messages); edges are the branching
   structure. Derived, regenerable.
3. **Kept nodes.** User-flagged. Promoted out of a session into
   long-term storage. **The durable artifact — the knowledge base
   the user is actually building.** This is the only layer the user
   actively curates.

The kept-node layer is what the previous card atlas was trying to be,
but reached by harvesting real exploration instead of by upfront
schema design. **The card emerges from the chat, not the other way
around.**

### A prior prototype already failed — and the lessons matter

A previous prototype tried roughly this (LLM answers + 3 follow-up
branches as JSON). It failed for two reasons:

**1. Drift from the original question.** After 5 hops the conversation
had nothing to do with where it started. The model treated each turn
as local — "user asked about analog VLSI? Here are 3 branches off
analog VLSI" — and three hops later was deep in MOSFET physics with
the root question forgotten.

This is a **design problem, not a model problem.** Even a frontier
model would drift if the prompt only carries the immediate parent.
Three fixes, increasing in ambition:

- **Root question always in context.** Every prompt includes the
  original root question, verbatim, with a directive: *propose
  follow-ups that bring the conversation closer to answering it, not
  further from it.* Solves most drift on its own.
- **Branches are typed, not free.** Instead of "propose 3 follow-ups,"
  ask for one of each type:
  - *deeper* — mechanism, detail, next layer down
  - *lateral* — alternative, contrast, analogy
  - *return-to-root* — how does this answer the original question?
  The third type is the anti-drift constraint, structurally enforced.
  Queneau again: constraint as navigation.
- **Periodic re-anchoring.** Every ~5 turns, an LLM-written "where we
  are vs. where we started" check, surfaced as a card on the map.
  The drift becomes visible.

**2. Hallucination and made-up coherence.** Mistral Medium was part
of it, but not the whole story. Three things to separate:

- *Hallucinated facts* — RAG fixes this.
- *Hallucinated branches* — the LLM proposes "explore the connection
  between Loihi and quantum computing" when there isn't one. Worse
  than hallucinated facts because it sends the user down a fake path.
  Partial fix: retrieval-supported branches only (see below).
- *Hallucinated coherence* — the silent failure. The model keeps the
  prose flowing past the point where it actually knows anything. Chat
  interfaces are uniquely bad at exposing this; the redesign must.

### The fix: every answer is a citation, every branch is a card

The card-graph instinct from the main pivot pays off here, but **as
the substrate the chat draws from, not as a thing the user browses.**

Concrete shape of the answering pipeline:

```
user question + root question + parent context
  ↓
retrieve (corpus first, web fallback)
  ↓
LLM call: answer with inline citations;
          propose 3 typed branches (deeper / lateral / return)
          each annotated with candidate-source count
  ↓
render: answer with hover citations,
        branches with grounding badges
  ↓
on "keep": distill node into a card, add to corpus
```

- **Every claim cites a chunk.** Inline `[1]`, `[2]`, sources visible
  on hover.
- **Every branch is annotated with grounding.** "4 candidate sources"
  vs. "no corpus support — would need web search." The user *sees*
  which branches are speculative.
- **A branch with zero sources is allowed but flagged.** Clicking it
  triggers an explicit search pass. The user knows they're going
  off-map.

This puts the hallucination problem **in front of the user**, instead
of hiding it behind fluent prose.

### Drift made visible, not just suspected

The map nodes carry an embedding-distance from the root question.
Visualized as edge length, node color, or a small badge. **Nodes far
from the root pull visually away.** The user gets a literal picture
of "I've wandered" — and can decide whether that wandering is
intentional or accidental.

This is the move that makes the redesign more than chat-plus-sidebar:
**the map is annotated with grounding and drift, both of which are
invisible in chat.** Two signals chat strips out, restored in the
external view.

### The corpus that grows from the session

RAG needs something to retrieve from. Three modes:

1. **Web-only.** Every query triggers search. High latency, drift
   risk high, but zero setup.
2. **Curated corpus + web fallback.** The existing wiki catalogue
   becomes the seed corpus. **The current project's output becomes
   the new project's input.** That re-uses everything that's already
   been built without forcing the user into it.
3. **Corpus that grows from the session.** Pages retrieved during a
   session get distilled into local cards, added to the corpus,
   available next session. **The knowledge base accumulates as a
   side effect of exploration.**

Mode 3 is the structural answer to "chat doesn't accumulate." Not
just the *map* persists — **the corpus the LLM retrieves from grows
with each session.** A year of use produces a corpus tailored to the
questions actually asked. The knowledge base is harvested from real
exploration, not curated by hand.

### How this relates to the question-graph pivot above

The chat-first redesign and the question-graph pivot are **the same
machine seen from opposite ends.**

- The question-graph pivot says: given a curated card layer, build
  a rhetorical layer on top, then walk it for any reader's question.
  **Top-down.**
- The chat-first redesign says: let readers ask questions, log their
  walks, and harvest the resulting structure as both a map (the
  question graph emerging) and a kept-card library (the cards
  emerging). **Bottom-up.**

Both arrive at the same two-graph model — cards underneath, argument
structure above — but they differ in **whether the structure is
designed first and consumed, or used first and accreted.** That's a
real fork in the road, and it's worth being explicit about which
direction is being chosen.

A reasonable hybrid: **chat-first as the user surface, question-graph
as the long-term shape.** The chat-first interface is what someone
actually opens. Behind it, kept nodes accumulate; over time, they
get reorganized (by the user, or by another agent pass) into the
question graph proper. The chat is the input loop; the graph is the
output artifact. Neither replaces the other.

### Revised prototype, in light of the prior failure

Same UX as the naive prototype that failed, but with the four lessons
baked in:

1. **Typed branches** (deeper / lateral / return-to-root) instead of
   free-form follow-ups.
2. **Root question pinned in every prompt**, with explicit instruction
   to relate the answer back to it.
3. **Mandatory citations** from a retrieval pass. Answers without
   sources are refused, not faked.
4. **Drift indicator** on each node (embedding distance from root,
   visualized on the map).

Stretch goals, only after the four above work:

- **Periodic re-anchoring card** every ~5 turns.
- **Branches annotated with candidate-source counts.**
- **"Keep" promotes a node into a growing corpus** that future
  sessions retrieve from.

The honest open question this redesign doesn't resolve: **how good
does the drift visualization need to be to feel useful?** Embedding
distance is a crude proxy. Probably needs to be paired with an
explicit periodic check — *"still on track?"* — rather than relying
purely on the visual. To be answered by the prototype.

### What this means for the current codebase

Not necessarily a throw-away. The existing pieces map onto the new
shape:

- The card catalogue → the **seed corpus** for RAG.
- The axes → optional **filters on retrieval** (still useful for
  scoping a session, not as primary navigation).
- The edges (when built) → **boost signal for retrieval** ("the
  current node is about Mead; pull in entries related to him").
- The dev server, prompts, build-index → **largely reusable** as the
  backend of the new interface.
- The frontend grid → **either deprecated, or kept as a secondary
  "browse the corpus" view** alongside the chat-first primary surface.

The chat-first surface would be a new frontend page, sharing the
same Flask backend. **It can be built alongside the current grid
view, not in place of it.** Whichever surface gets used more, wins.
That's a cheaper experiment than committing to either direction now.

### One-line synthesis (revised)

**Chat is the right interface for asking; a map is the right
interface for remembering. Build both surfaces over a single corpus
that grows from real questions, and the knowledge base accumulates
as a side effect of being curious.**
