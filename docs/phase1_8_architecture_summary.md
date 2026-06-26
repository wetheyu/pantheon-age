# Phase 1-8 Architecture Summary

This document consolidates the completed Phase 1-8 work into the current
architecture baseline.

It is the main structure map before Phase 9 Web UI work starts.

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
程序负责规避 LLM 的缺点：上下文漂移、逻辑不统一、记忆不稳定、容易乱给奖励。
规则限制的是“能不能改写现实”，不是“能不能想象内容”。
```

## Current Runtime Shape

The current playable world-mode path is:

```text
Player input
  -> CLI or API entry
  -> phase1_cli.game_service
  -> Agentic Runtime world-mode loop
  -> context pack
  -> canon retrieval + memory retrieval
  -> Creative GM / Turn Director / local fallback provider
  -> validators
  -> state commit
  -> memory / generated fact / relationship commit helpers
  -> persistence
  -> player-facing narration
```

The important distinction:

```text
Narration can suggest.
State Commit decides what happened.
Memory Commit decides what becomes durable.
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
- `phase1_cli/progression.py` and `phase1_cli/items.py` now provide Phase 8
  mechanical helpers.

Do not use Phase 1 keyword parsing as the long-term world-mode design. It is a
fallback/tutorial path.

## Phase 2: FastAPI Service Layer

Purpose:

- expose the reusable game service through HTTP;
- prepare for external clients and the future web UI;
- keep route handlers thin.

Current role:

- `phase2_api/main.py` creates the FastAPI app;
- `phase2_api/routes/` contains resource routes;
- `phase2_api/schemas.py` is the request/response boundary;
- `phase2_api/services/session_store.py` adapts API sessions to persistence.

Phase 9 should improve this layer for browser play, but should not move game
rules into routes.

## Phase 3: SQLite Persistence

Purpose:

- persist sessions, events, and long-term memory;
- support API game sessions beyond process memory;
- provide a simple local database before any heavier infrastructure.

Current role:

- `phase3_persistence/sqlite_repository.py` stores sessions, event logs, and
  memory records;
- `phase3_persistence/config.py` owns persistence config;
- SQLite remains the right default for local development.

Do not introduce PostgreSQL or distributed storage until Phase 9/10 proves the
need.

## Phase 4: Structured LLM Runtime Bridge

Purpose:

- introduce structured LLM proposal contracts;
- test provider boundaries;
- prove validation before narration/commit.

Current role:

- `llm_runtime/` is a compatibility and learning layer;
- `phase1_cli.game_service` still uses it for non-Agentic tutorial/legacy paths;
- tests still cover it.

Do not delete it yet. Do not expand it as the primary gameplay path.

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

## Canonical Entry Points

Use these as the primary references:

- `AGENTS.md`: engineering rules and long-term boundaries.
- `README.md`: project overview and run commands.
- `docs/README.md`: documentation index.
- `docs/phase1_8_architecture_summary.md`: current architecture baseline.
- `docs/agentic_runtime_architecture.md`: long-term agent architecture.
- `docs/phase6_completion_summary.md`: world knowledge and memory details.
- `docs/phase7_completion_summary.md`: playability calibration details.
- `docs/phase8_completion_summary.md`: progression/core mechanics details.
- `docs/future_phase_plan.md`: Phase 9/10 execution plan.
- `docs/world_bible.md`: readable world overview.
- `docs/canon/`: retrievable canon corpus.
- `docs/progression_design.md`: mechanics design source.

## Historical Or Compatibility References

These are still useful, but should not override the current baseline:

- `docs/phase2_api_plan.md`: Phase 2 API planning history.
- `docs/phase4_llm_runtime_plan.md`: Phase 4 structured runtime history.
- `docs/phase5_agentic_runtime_plan.md`: Phase 5 build history.
- `docs/phase6_world_memory_plan.md`: Phase 6 build history.
- `docs/system_design.md`: learning-oriented system design notes.
- `docs/technical_roadmap.md`: broad long-term technical notes.
- `docs/rag_seed_cards.md`: fallback compact lore cards.
- `llm_runtime/`: Phase 4 compatibility layer and tests.

## Cleanup Decisions

Safe to keep:

- `llm_runtime/`, because tutorial/legacy service paths and tests still use it.
- `docs/rag_seed_cards.md`, because context packing still uses it as fallback.
- `docs/tone_guide.md`, because older prompts and canon references still point
  to it.
- local `data/*.sqlite3` and `saves/*.json`, because they are ignored runtime
  artifacts.

Removed/renamed:

- the old `docs/phase1_6_architecture_summary.md` baseline has been replaced by
  this Phase 1-8 summary.

Do not delete runtime code merely because it is not the primary path. Deletion
should follow tests and references, not taste.

## Handoff To Phase 9

Phase 9 should not invent new game rules.

It should productize the current runtime:

- expose clean API shapes for world-mode creation and actions;
- make browser play more readable than CLI;
- surface roll breakdown, current scene, inventory, abilities, advancement
  options, and committed effects;
- keep debug/runtime traces hidden unless explicitly requested;
- keep all state mutation behind the existing service/runtime/commit layers.
