# Future Phase Plan

This document is the execution-oriented roadmap after Phase 5.

Core direction:

```text
LLM provides imagination.
The program provides memory, consistency, validation, persistence, and speed.
Build stable knowledge and memory foundations before polishing final play feel.
```

Do not treat this as a rigid contract. Each phase should be reviewed after real
playtesting. If a later phase changes the input structure of the LLM runtime,
avoid spending too much effort polishing the old experience first.

## Consolidated Phase Roadmap

Use this consolidated order:

```text
Phase 6: World Knowledge And Persistent Memory
Phase 7: Minimum Playable Experience Calibration
Phase 8: Progression And Core Mechanics
Phase 9: Web UI And API Product Experience
Phase 10: Engineering Quality And Final Experience Optimization
```

Why Phase 6 and Phase 7 are ordered this way:

```text
RAG and world memory change what the LLM receives.
They affect Turn Director prompts, context packing, persistence, and narration.
Therefore implement the knowledge/memory foundation first, then polish the
player experience on top of the new runtime shape.
```

Cross-cutting rule:

```text
Every phase should include basic tests, safety checks, and docs updates.
Do not save observability, evals, or performance thinking for the very end.
```

## Phase 6: World Knowledge And Persistent Memory

Goal: give LLMs the right world information and let the world remember validated
facts beyond a single scene.

This phase merges RAG and persistent world memory because they are two sides of
the same system:

- static canon: countries, cities, gods, churches, classes, tone, policy;
- dynamic memory: generated NPCs, location memories, relation changes,
  committed events, player-known facts, and hidden facts.

Main work:

- split world canon into smaller Markdown files;
- define metadata: country, city, god, church, class, tone, policy, visibility;
- build a local chunker and keyword/BM25-like retriever first;
- add embeddings only after simple retrieval becomes insufficient;
- persist generated but validated NPCs, locations, rumors, events, and faction
  changes;
- add visibility levels: player-known, NPC-known, faction-known, system-secret;
- add memory summarization so context does not grow forever.

Suggested stages:

### Phase 6.1 Canon Corpus Split

- Split `docs/world_bible.md` into topic files under a canon folder.
- Keep `world_bible.md` as a readable overview.
- Add simple metadata headers.
- Keep inspiration notes separate from canon facts.

Done when:

- countries, gods, churches, classes, tone, and forbidden-output docs can be
  retrieved independently.

### Phase 6.2 Local Retriever

- Build deterministic local retrieval over Markdown chunks.
- Return only top relevant chunks to Turn Director.
- Add tests for country, city, church, god, class, and tone retrieval.
- Replace ad hoc lore-card retrieval only when the new retriever is stable.

Done when:

- obvious queries retrieve the right canon chunks without dumping huge docs into
  each LLM call.

### Phase 6.3 Persistent Memory Schema

- Move memory storage from `GameState.agentic_memory` toward persistence-layer
  tables or structured snapshots.
- Keep SQLite first.
- Preserve visibility boundaries.
- Do not persist raw LLM output directly as truth.

Done when:

- validated player-known and hidden memory can survive save/load and API session
  persistence.

### Phase 6.4 Generated Fact Commit

- Add a validator for turning temporary content into persistent world facts.
- Persist recurring NPCs, locations, relation signals, and committed rumors only
  after validation.
- Keep temporary generated content cheap and disposable.

Done when:

- an NPC, rumor, or local event can become persistent only through an explicit
  validated commit.

### Phase 6.5 Relationship And Faction Memory

- Store NPC attitude, faction pressure, church legality changes, and nation
  relation signals.
- Keep relation changes as evidence-backed deltas, not arbitrary rewrites.

Done when:

- church/nation/NPC relationship changes can accumulate over multiple turns.

### Phase 6.6 Memory Summarizer

- Summarize committed history without adding new facts.
- Never summarize hidden memory into player-visible context by accident.
- Keep summaries short enough for Turn Director prompts.

Done when:

- long sessions can continue without context growing uncontrollably.

### Phase 6.7 Embedding Retriever

- Add embeddings behind a provider boundary only after local retrieval works.
- Start with local files or SQLite storage.
- Consider pgvector only when PostgreSQL becomes necessary.

Done when:

- retrieval quality improves without breaking visibility or authority rules.

Non-goals:

- final UX polish;
- full web UI;
- full progression system;
- production deployment.

## Phase 7: Minimum Playable Experience Calibration

Goal: make the world-mode game minimally comfortable to test after the knowledge
and memory foundation is in place.

Why this comes after Phase 6:

RAG and persistent memory will change context shape, prompt content, latency,
and narrative grounding. Phase 7 should not be final polish. It should only make
the game clear enough to test Phase 8 and Phase 9 without fighting the CLI.

Main work:

- reduce obviously bad LLM latency and prompt bloat after real retrieval is integrated;
- improve Turn Director output enough for repeatable playtests;
- make high-risk actions show clear dice math and consequences;
- improve opening introduction, player identity, and first-scene hooks;
- make CLI feel like a tabletop chat instead of a debug console;
- add a simple playtest checklist and regression fixtures.

Suggested stages:

### Phase 7.1 Basic Runtime Speed Pass

- Keep Turn Director as the default live path.
- Shrink Turn Director schema further if needed.
- Add optional `PANTHEON_FAST_MODE=1` for shorter narration and lower token use.
- Record per-turn latency in debug mode only.
- Compare model choices through a small live smoke script.

Done when:

- one normal world-mode turn succeeds without fallback;
- runtime report can show elapsed time when enabled;
- normal tests still do not call the network.

### Phase 7.2 Basic Story Output Pass

- Make narration more like a game master response.
- Remove mechanical or awkward filler from player-facing text.
- Ensure NPC speech, scene pressure, and next-action hooks are clear.
- Make dice results appear only when a real check occurs.

Done when:

- a 5-turn CLI playtest reads like a coherent scene;
- no runtime/debug labels appear unless `PANTHEON_SHOW_RUNTIME=1`.

### Phase 7.3 Opening And Player Onboarding

- Polish world-mode introduction.
- Make selected class, faith, country, ethnicity, city, and identity matter in
  the opening text.
- Offer a few natural first actions without forcing button choices.

Done when:

- a new player knows who they are, where they are, and what kinds of things they
  can try.

### Phase 7.4 Live Playtest Fixtures

- Add a small set of scripted sample turns.
- Add expected safety properties, not exact story text.
- Cover violence, social inquiry, occult investigation, stealth, prayer, and
  travel attempt.

Done when:

- the project has a repeatable playtest checklist before Phase 8.

Non-goals:

- full vector RAG redesign;
- major database redesign;
- web UI;
- full progression system;
- final balance or final UX polish.

## Phase 8: Progression And Core Mechanics

Goal: turn the character sheet into a meaningful game system.

Main work:

- implement the six-attribute model from `docs/progression_design.md`;
- add class level and faith level;
- add skills, talents, prayers, favor, revelation, and burdens in small slices;
- add ritual promotion requirements;
- define item categories and equipment effects;
- improve checks for combat, stealth, social pressure, occult risk, and travel.

Suggested stages:

### Phase 8.1 Character Model Migration Plan

- Design save/API compatibility before changing fields.
- Decide how current four stats migrate to six attributes.

### Phase 8.2 Minimal Leveling Slice

- Add class level and faith level.
- Add one skill per class and one prayer per god.
- Add tests for serialization and public state.

### Phase 8.3 Ritual And Cost Slice

- Add ritual promotion as a validated proposal.
- Add costs such as corruption, suspicion, debt, burden, or faction pressure.

### Phase 8.4 Item And Equipment Slice

- Add item categories.
- Allow temporary generated items to become real only after validation and
  explicit commit.

Done when:

- character choices create different options in play;
- leveling is explainable in interviews and visible in gameplay.

## Phase 9: Web UI And API Product Experience

Goal: make the game playable outside the terminal.

Main work:

- React + TypeScript + Vite frontend;
- chat-style story panel;
- player input box;
- character sheet;
- status, inventory, clues, memory, and event log panels;
- API client for FastAPI endpoints;
- API response polish for world-mode and agentic runtime output;
- loading states and friendly error display.

Suggested stages:

### Phase 9.1 Minimal Chat UI

- Start a web app.
- Connect to existing FastAPI endpoints.
- Create a game and submit actions.

### Phase 9.2 Game Panels

- Add character, status, inventory, clues, and memory panels.
- Keep UI display-only for state. Rules stay backend-side.

### Phase 9.3 API Product Polish

- Make world-mode create-game and action endpoints comfortable for frontend use.
- Keep runtime debug data hidden unless requested.
- Add readable API errors for LLM timeout, fallback, and validation failure.

### Phase 9.4 Streaming Or Loading UX

- Add loading state first.
- Consider streaming narration later if provider support and architecture are
  ready.

Done when:

- a user can play the current world-mode loop in a browser.

## Phase 10: Engineering Quality And Final Experience Optimization

Goal: make the project debuggable, safer, reproducible, portable, and optionally
cheaper to run, then perform the final broad gameplay polish pass.

Main work:

- structured traces for LLM calls;
- token, cost, latency, fallback, and validator logs;
- eval fixtures for safety and story quality;
- prompt injection tests;
- model comparison scripts;
- Docker / Docker Compose;
- environment profiles for local, dev, and production;
- optional local model provider through OpenAI-compatible APIs;
- database migration strategy;
- deployment notes.
- final gameplay pacing, balance, model choice, prompt quality, and web/CLI
  experience polish.

Suggested stages:

### Phase 10.1 Trace Records

- Store prompt name, model, latency, output validity, fallback reason, and
  validator decision.

### Phase 10.2 Safety Evals

- Test that LLM does not invent gods, grant free items, reveal secrets, confirm
  deaths, or mutate protected state.

### Phase 10.3 Quality Evals

- Add sample scenes and score broad properties: coherence, next hook, canon
  consistency, and player agency.

### Phase 10.4 Dockerized API

- Containerize FastAPI service.
- Keep `.env` secret handling clear.

### Phase 10.5 Local Model Provider

- Add `OPENAI_BASE_URL` or equivalent provider config.
- Test with a local OpenAI-compatible server.
- Keep the same validators.

### Phase 10.6 Production Deployment

- Add persistent database config.
- Add basic health checks and startup docs.

### Phase 10.7 Final Experience Optimization

- Review speed, cost, story quality, profession/faith balance, UI comfort, and
  long-session memory behavior together.
- Tune prompts, model choices, schema size, progression balance, and playtest
  fixtures.
- Decide what is demo-ready for resume/interview presentation.

Done when:

- regressions in agent behavior are visible before manual playtesting;
- another machine can run the API and optional web UI with documented setup;
- the project has one polished demo path suitable for showing to others.

## Recommended Next Step

Start Phase 6: World Knowledge And Persistent Memory.

Reason:

The next large architectural change is how the runtime retrieves canon and
remembers validated world facts. It will change Turn Director prompts, context
packing, persistence, and narration grounding. Build that foundation first, do
minimum playability calibration in Phase 7, then save final experience polish for
Phase 10.
