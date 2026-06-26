# Phase 1-9 Architecture Summary

This document consolidates the completed Phase 1-9 work into the current
architecture baseline.

It is the main structure map before the final Phase 10 quality and demo pass.

## Core Principle

```text
LLM provides imagination.
The program provides authority, memory, validation, retrieval, persistence, and speed control.
Rules constrain authority, not imagination.
Only validated structured state becomes game truth.
```

In plain Chinese:

```text
LLM 负责想象力。
程序负责规避 LLM 的缺点：上下文漂移、逻辑不统一、长期记忆弱、容易乱给奖励。
规则限制的是“能不能改写现实”，不是“能不能想象内容”。
```

## Current Runtime Shape

The current playable browser/world-mode path is:

```text
Browser or CLI input
  -> FastAPI route or CLI entry
  -> phase1_cli.game_service
  -> Agentic Runtime world-mode loop
  -> context pack
  -> canon retrieval + memory retrieval
  -> Creative GM / Turn Director / local fallback provider
  -> validators
  -> state commit
  -> memory / generated fact / relationship commit helpers
  -> SQLite persistence
  -> API response or CLI response
  -> player-facing story and public state
```

The important distinction:

```text
Narration can suggest.
State Commit decides what happened.
Memory Commit decides what becomes durable.
The browser displays state; it does not execute rules.
```

## Phase 1: Python CLI Core

Purpose:

- prove the minimum text-adventure loop;
- keep a deterministic tutorial mode;
- provide reusable state, character, save/load, and service primitives.

Current role:

- `phase1_cli/main.py` is CLI-only input/output;
- `phase1_cli/game_service.py` is the shared action service used by CLI/API;
- `phase1_cli/rule_engine.py` remains the deterministic tutorial engine;
- `phase1_cli/game_state.py` and `phase1_cli/character.py` are core state
  models;
- `phase1_cli/scenarios.py` handles tutorial/world-mode setup;
- `phase1_cli/progression.py` and `phase1_cli/items.py` provide Phase 8
  mechanical helpers.

Do not use Phase 1 keyword parsing as the long-term world-mode design. It is a
fallback/tutorial path.

## Phase 2: FastAPI Service Layer

Purpose:

- expose the reusable game service through HTTP;
- prepare external clients and the browser UI;
- keep route handlers thin.

Current role:

- `phase2_api/main.py` creates the FastAPI app and CORS setup;
- `phase2_api/routes/` contains resource routes;
- `phase2_api/routes/origins.py` exposes world-mode setup options;
- `phase2_api/schemas.py` is the request/response boundary;
- `phase2_api/services/session_store.py` adapts API sessions to persistence.

Route handlers should stay thin. Rules, dice, memory, validation, and state
mutation must stay behind the service/runtime layers.

## Phase 3: SQLite Persistence

Purpose:

- persist sessions, events, and long-term memory;
- support API game sessions beyond process memory;
- provide a simple local database before heavier infrastructure.

Current role:

- `phase3_persistence/sqlite_repository.py` stores sessions, event logs, and
  memory records;
- `phase3_persistence/config.py` owns persistence config;
- SQLite remains the right default for local development and demos.

Do not introduce PostgreSQL or distributed storage until Phase 10 packaging or
deployment requirements prove the need.

## Phase 4: Structured LLM Runtime Bridge

Purpose:

- introduce structured LLM proposal contracts;
- test provider boundaries;
- prove validation before narration/commit.

Current role:

- `llm_runtime/` is a compatibility and learning layer;
- older smoke/live tests still cover it;
- some tutorial/legacy service paths still reference it.

Do not expand Phase 4 as the primary gameplay path. The main world-mode path is
Agentic Runtime.

## Phase 5: Agentic Runtime Baseline

Purpose:

- make world-mode gameplay agentic;
- preserve open player intent;
- separate imagination from authority.

Canonical files:

- `agentic_runtime/orchestrator.py`
- `agentic_runtime/providers.py`
- `agentic_runtime/contracts.py`
- `agentic_runtime/validators.py`
- `agentic_runtime/state_commit.py`
- `agentic_runtime/context_pack.py`
- `agentic_runtime/memory_*`
- `agentic_runtime/generated_facts.py`
- `agentic_runtime/relationship_memory.py`

Boundary:

```text
Agents propose.
Validators reject unsafe proposals.
State Commit writes game reality.
Memory Commit writes durable world facts.
```

Preferred live-play path:

```text
PANTHEON_USE_AGENTIC_LLM=1
PANTHEON_CREATIVE_GM_MODE=1
PANTHEON_AGENTIC_TURN_DIRECTOR=1
PANTHEON_AGENTIC_FULL_LLM=0
```

This lets one LLM call own player-facing imagination while Python keeps memory,
dice, validation, and state authority.

## Phase 6: World Knowledge And Persistent Memory

Purpose:

- ground agents in world canon;
- retrieve relevant context instead of dumping whole docs;
- remember validated facts over time.

Canonical files:

- `docs/canon/`
- `rag/canon.py`
- `rag/embeddings.py`
- `rag/vector_store.py`
- `agentic_runtime/memory_retriever.py`
- `agentic_runtime/memory_summarizer.py`
- `phase3_persistence/sqlite_repository.py`

Current behavior:

- local keyword/hybrid retrieval works offline;
- optional OpenAI embeddings are supported;
- SQLite vector cache is available;
- memory visibility separates player-known, NPC-known, faction, location,
  quest, and secret records.

## Phase 7: Minimum Playable Experience Calibration

Purpose:

- make world-mode feel playable in CLI;
- reduce runtime report flavor;
- enforce scene continuity and risk clarity;
- make manual playtests repeatable.

Current baseline:

- opening/profile setup differs by origin, city, class, faith, and background;
- `current_location` is city-level truth;
- `current_scene_focus` is concrete local scene truth;
- non-movement actions do not teleport the player;
- risky actions show visible dice math;
- violence, social, stealth, theft, escape, occult, and generic high-risk
  actions have distinct consequence shapes;
- Creative GM mode is the preferred live LLM play path;
- local playtest fixtures cover the safety path without network calls.

## Phase 8: Progression And Core Mechanics

Purpose:

- make character choices matter mechanically;
- add rule-owned progression without turning rules into a creativity ceiling.

Current baseline:

- six attributes: Physique, Agility, Insight, Knowledge, Will, Communion;
- class level, faith level, ascension rank, Revelation, Favor, Devotion;
- one Lv1 class skill per class;
- one Lv1 faith talent and prayer per god;
- generic world-mode check profiles using six attributes;
- prayer costs and blocked prayer handling;
- religion legality pressure for restricted/hostile faith use;
- class, faith, and first ascension advancement gates;
- item affordances, item bonuses, direct consumable use, and consumable costs;
- status/help output explains current Phase 8 capabilities.

Phase 8 is a baseline, not final balance.

## Phase 9: API And Web Product Baseline

Purpose:

- make the current game loop playable from a browser;
- expose world-mode setup choices through API;
- keep frontend display-only for rules and state mutation;
- prove the project can be presented as a product slice.

Canonical files:

- `phase2_api/routes/origins.py`
- `phase2_api/routes/games.py`
- `phase2_api/schemas.py`
- `phase2_api/services/session_store.py`
- `web_ui/src/api.ts`
- `web_ui/src/main.tsx`
- `web_ui/src/types.ts`
- `web_ui/src/styles.css`
- `web_ui/scripts/api-smoke.mjs`

Current baseline:

- `GET /origins` exposes playable origin countries, cities, ethnicities, and
  backgrounds;
- `POST /games` can create world-mode games from browser setup;
- `POST /games/{game_id}/actions` returns story, public state, mechanics,
  optional debug, and legacy response;
- browser can create a world-mode character, submit actions, show story log,
  display character/world panels, use opening action suggestions, and restart;
- `npm run smoke:api` checks the main API/web path while FastAPI is running.

The browser must not duplicate rules, dice, validators, memory, or state commit.

## Main Entry Points

Use these as the primary references:

- `AGENTS.md`: engineering rules and long-term boundaries.
- `README.md`: project overview and run commands.
- `docs/README.md`: documentation index.
- `docs/phase1_9_architecture_summary.md`: current architecture baseline.
- `docs/final_phase10_plan.md`: final phase execution plan.
- `docs/agentic_runtime_architecture.md`: long-term agent architecture.
- `docs/live_llm_testing.md`: safe live LLM testing workflow.
- `docs/world_bible.md`: readable world overview.
- `docs/canon/`: retrievable canon corpus.
- `docs/progression_design.md`: mechanics design source.

## Historical Or Compatibility References

These are still useful, but should not override the current baseline:

- `docs/phase2_api_plan.md`: Phase 2 API planning history.
- `docs/phase4_llm_runtime_plan.md`: Phase 4 structured runtime history.
- `docs/phase5_agentic_runtime_plan.md`: Phase 5 build history.
- `docs/phase6_world_memory_plan.md`: Phase 6 build history.
- `docs/phase6_completion_summary.md`: Phase 6 completion details.
- `docs/phase7_completion_summary.md`: Phase 7 completion details.
- `docs/phase8_completion_summary.md`: Phase 8 completion details.
- `docs/system_design.md`: learning-oriented system design notes.
- `docs/technical_roadmap.md`: broad long-term technical notes.
- `docs/rag_seed_cards.md`: fallback compact lore cards.
- `docs/phase9_10_execution_plan.md`: completed Phase 9 plus initial Phase 10
  plan history.
- `llm_runtime/`: Phase 4 compatibility layer and tests.

## Cleanup Decisions

Safe to keep:

- `llm_runtime/`, because tutorial/legacy service paths and tests still use it.
- `docs/rag_seed_cards.md`, because context packing still uses it as fallback.
- `docs/tone_guide.md`, because prompts and canon references still point to it.
- local `data/*.sqlite3` and `saves/*.json`, because they are ignored runtime
  artifacts.

Renamed:

- `docs/phase1_8_architecture_summary.md` has been replaced by this Phase 1-9
  summary.

Do not delete runtime code merely because it is not the primary path. Deletion
should follow tests and references, not taste.

## Handoff To Final Phase 10

Phase 10 should not invent a second game system.

It should make the current runtime:

- observable;
- eval-tested;
- faster and cheaper;
- easier to run;
- easier to demo;
- safe for live LLM experiments;
- presentable as a resume-friendly AI Agent project.

The next document to follow is:

```text
docs/final_phase10_plan.md
```
