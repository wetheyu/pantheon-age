# Project Architecture

This document is the current high-level architecture map for Pantheon Age.

It should be read before older phase documents. Phase documents explain how the
project arrived here; this document explains how the project is organized now.

## Core Idea

```text
LLM creates possibilities.
The program controls authority.
Only validated structured changes become game truth.
```

In practical terms:

- LLMs may imagine actions, scenes, NPCs, events, items, and prose.
- Python validates whether those proposals are allowed.
- Dice, resources, state changes, memory writes, rewards, deaths, clues, and
  location changes must pass program-side authority boundaries.
- RAG and memory give context to the LLM, but they do not replace rules.

## Main Runtime Flow

The current player-facing world-mode path is:

```text
CLI or Browser
  -> phase1_cli.game_service
  -> agentic_runtime.orchestrator
  -> context_pack
  -> canon retrieval + memory retrieval
  -> LLM provider or local fallback provider
  -> validators
  -> state_commit
  -> memory / generated fact / relationship commit helpers
  -> persistence
  -> player-facing story + public state
```

The browser path adds FastAPI before `game_service`:

```text
Browser
  -> phase2_api routes
  -> phase2_api services/session_store
  -> phase1_cli.game_service
  -> Agentic Runtime
  -> SQLite repository
  -> JSON response
  -> React UI
```

## Directory Responsibilities

```text
phase1_cli/
  Reusable game core, CLI entry point, character/state models, tutorial rule
  engine, world-mode service orchestration hooks, progression and item helpers.

phase2_api/
  FastAPI app, route handlers, request/response schemas, API session service.
  Route handlers should stay thin.

phase3_persistence/
  SQLite repository, database config, persistence errors, session/event/memory
  storage.

agentic_runtime/
  Current main LLM-agent gameplay runtime. Handles context packing, provider
  selection, validation, state commit, memory commit, observability, performance
  profile, safety evals, quality evals, playtest fixtures, and final demo smoke.

llm_runtime/
  Earlier structured LLM compatibility layer. Keep it stable for tests and
  learning, but do not expand it as the main gameplay path.

rag/
  Canon document loading, keyword retrieval, embedding provider boundary, and
  SQLite vector cache.

prompts/
  Versioned prompt and policy text for LLM roles.

docs/
  Public project docs, world canon, architecture, plans, runbooks, and demo
  instructions.

docs/canon/
  Split world-canon corpus used by retrieval.

tests/
  Unit tests, safety evals, narrative quality evals, playtest fixtures, API
  contract tests, persistence tests, and opt-in live LLM tests.

web_ui/
  React + TypeScript + Vite browser playtest client.

scripts/
  Local developer command helper.
```

## Authority Boundaries

The most important rule is not "LLM cannot be creative." The rule is:

```text
LLM cannot commit reality by itself.
```

Examples:

- The LLM can describe a guard blocking the player.
- The LLM cannot decide the guard is dead unless the validated rule result
  permits it.
- The LLM can describe a suspicious letter.
- The LLM cannot add that letter to inventory unless state commit allows it.
- The LLM can describe a wealthy estate.
- The LLM cannot grant ownership if the player lacks resources or a validated
  acquisition path.
- RAG can tell the model what 卢塞恩 is.
- RAG cannot authorize a clue, reward, city change, or relationship change.

## Current Main Components

### Game Service

`phase1_cli/game_service.py` is the reusable game-action boundary.

It receives player input and returns structured `GameResponse` data that can be
printed by CLI or serialized by FastAPI.

### Agentic Runtime

`agentic_runtime/orchestrator.py` coordinates the world-mode turn.

The important supporting modules are:

- `context_pack.py`: builds compact context from state, canon, and memory.
- `providers.py`: chooses local provider, OpenAI provider, creative GM path, or
  fallback path.
- `validators.py`: blocks unsafe or unauthorized proposals.
- `state_commit.py`: writes validated state changes.
- `memory_curator.py`: decides what memory candidates are worth storing.
- `memory_retriever.py`: retrieves visible long-term memory.
- `world_slice.py`: builds city/origin/religion context.
- `observability.py`: creates safe debug summaries without secrets.
- `runtime_profiles.py`: defines local/fast/quality/debug runtime behavior.
- `safety_evals.py`: checks authority-boundary regressions.
- `narrative_quality_evals.py`: checks player-facing prose quality.
- `final_demo.py`: checks the final portfolio demo route.

### Progression And Checks

The current character check model uses six attributes:

```text
physique   physical force, endurance, direct combat
agility    stealth, theft, evasion, quick movement
insight    observation, social reads, investigation
knowledge  archives, occult theory, medicine, engineering
will       pressure resistance, discipline, vows
communion  prayer, ritual contact, divine pressure
```

World-mode checks use `risk_type + check_attribute`, then convert the selected
attribute through `attribute_modifier = (attribute - 10) // 2`.

Early four-stat save data is still readable for compatibility, but `stats` is
not the public state model, UI model, or LLM context model.

### RAG

`rag/canon.py` loads canon chunks from `docs/canon/` and retrieves relevant
cards.

Retrieval modes:

- keyword: stable, offline, cheap default;
- vector: embedding-based retrieval;
- vector_hybrid: combines lexical and vector signals;
- SQLite cache: stores vectors for repeat use.

### Persistence

`phase3_persistence/sqlite_repository.py` persists:

- game sessions;
- event logs;
- state snapshots;
- memory records.

SQLite is the right local default. PostgreSQL or pgvector should only be added
when deployment, multi-user usage, or corpus scale requires it.

### API

`phase2_api/` exposes the game through HTTP.

The route handlers should not contain game rules. They validate input, call the
service/session layer, and return response schemas.

### Web UI

`web_ui/` is a browser client for playtesting.

The UI should:

- collect player setup choices;
- submit actions;
- display story and public state;
- avoid duplicating rule logic;
- avoid exposing runtime/debug internals by default.

## What Is Legacy Or Compatibility

Some modules remain useful but should not be treated as the future main path:

- `phase1_cli/rule_engine.py`: deterministic tutorial engine and mechanical
  reference point.
- `phase1_cli/intent_parser.py`: tutorial/fallback parser, not the long-term
  open world-mode intent system.
- `llm_runtime/`: Phase 4 structured proposal bridge, useful for tests and
  compatibility, but not the current primary gameplay architecture.
- Older phase plan documents: useful history, not the source of current
  architecture truth.

## Recommended Reading Order

For understanding the project now:

1. `README.md`
2. `docs/project_architecture.md`
3. `docs/final_demo.md`
4. `docs/agentic_runtime_architecture.md`
5. `docs/system_design.md`
6. `docs/technical_roadmap.md`
7. `docs/world_bible.md`
8. `docs/progression_design.md`

For implementation:

1. `phase1_cli/game_service.py`
2. `agentic_runtime/orchestrator.py`
3. `agentic_runtime/context_pack.py`
4. `agentic_runtime/providers.py`
5. `agentic_runtime/validators.py`
6. `agentic_runtime/state_commit.py`
7. `phase3_persistence/sqlite_repository.py`
8. `phase2_api/routes/games.py`
9. `web_ui/src/main.tsx`

## Verification

Default local verification:

```bash
./.venv/bin/python scripts/dev.py check
./.venv/bin/python scripts/dev.py final-demo
./.venv/bin/python scripts/dev.py web-build
```

Live LLM tests must stay opt-in:

```bash
PANTHEON_RUN_LIVE_LLM_TESTS=1 ./.venv/bin/python -m unittest tests.test_live_agentic_runtime
```

Do not make normal tests depend on API cost, network access, or a real key.
