# Phase 1-6 Architecture Summary

This document consolidates the first six phases of `Pantheon Age` into the
current architecture baseline.

It replaces older direction notes that were useful during exploration but are no
longer the source of truth.

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

## Current Baseline

After Phase 6, the project is no longer just a CLI text adventure. It is now a
rule-stabilized Agentic Runtime foundation:

```text
Player input
  -> CLI or API entry
  -> phase1_cli.game_service
  -> Agentic Runtime world-mode loop
  -> context pack
  -> canon retrieval and memory retrieval
  -> Turn Director / local fallback providers
  -> validators
  -> state commit
  -> generated fact / relationship / memory commit helpers
  -> SQLite persistence
  -> player-facing narration
```

## Phase 1: Python CLI Core

Purpose:

- prove the minimum text-adventure loop;
- teach and preserve basic deterministic game structure;
- provide tutorial mode and a safe fallback path.

Keep:

- `phase1_cli/main.py` as CLI-only input/output;
- `phase1_cli/game_service.py` as reusable service orchestration;
- `phase1_cli/rule_engine.py` as deterministic tutorial rules;
- `phase1_cli/game_state.py` and `phase1_cli/character.py` as core state models.

Do not treat Phase 1 as the final gameplay model. The old fixed intent parser is
useful for tutorial/fallback behavior, but world-mode meaning should come from
Agentic Runtime.

## Phase 2: FastAPI Service Layer

Purpose:

- expose the reusable core through HTTP;
- prepare for web UI and external clients;
- keep API routes thin.

Keep:

- `phase2_api/main.py`;
- `phase2_api/routes/`;
- `phase2_api/services/session_store.py`;
- Pydantic schemas as API boundary objects.

Do not copy game logic into API routes. API code should call service/runtime
layers.

## Phase 3: SQLite Persistence

Purpose:

- persist game sessions, events, and later world memory;
- give API sessions and CLI saves a stronger foundation.

Keep:

- `phase3_persistence/sqlite_repository.py`;
- session/event persistence;
- Phase 6 memory persistence additions.

SQLite remains the right default for this stage. A larger database can wait
until API/web usage proves the need.

## Phase 4: Structured LLM Runtime Bridge

Purpose:

- introduce provider boundaries, prompts, structured proposals, and validators;
- prove that LLM output must be parsed and checked.

Current role:

- compatibility layer;
- smoke-test layer;
- useful reference for structured output and provider tests.

Do not expand Phase 4 as the main gameplay direction. The main live game path is
now Agentic Runtime.

## Phase 5: Agentic Runtime Baseline

Purpose:

- make LLM/agent logic the center of world-mode gameplay;
- preserve open player intent instead of forcing every action into narrow fixed
  command categories;
- let agents propose scenes, NPCs, events, items, adjudication, memory, and
  narration.

Canonical files:

- `agentic_runtime/orchestrator.py`;
- `agentic_runtime/providers.py`;
- `agentic_runtime/contracts.py`;
- `agentic_runtime/validators.py`;
- `agentic_runtime/state_commit.py`;
- `agentic_runtime/context_pack.py`;
- `prompts/turn_director.md`;
- `prompts/world_bundle.md`;
- `prompts/agentic_narrator.md`.

Important boundary:

```text
Agents may propose.
Validators may reject.
State Commit writes reality.
Memory commit writes durable world facts.
```

## Phase 6: World Knowledge And Persistent Memory

Purpose:

- give agents grounded world context;
- remember validated facts across turns;
- stop stuffing entire documents into prompts;
- prepare for real RAG and long sessions.

Canonical files:

- `docs/canon/`;
- `rag/canon.py`;
- `rag/embeddings.py`;
- `rag/vector_store.py`;
- `agentic_runtime/memory_retriever.py`;
- `agentic_runtime/memory_summarizer.py`;
- `agentic_runtime/generated_facts.py`;
- `agentic_runtime/relationship_memory.py`;
- `phase3_persistence/sqlite_repository.py`.

Phase 6 includes:

- split canon corpus;
- keyword and hybrid retrieval;
- optional real OpenAI embeddings;
- SQLite vector cache;
- persistent `game_memories`;
- generated fact commit;
- relationship/faction memory;
- bounded memory summarization.

## What Is Canonical Now

Use these documents as the main architecture entry points:

- `AGENTS.md`: long-term engineering rules.
- `README.md`: project overview and run commands.
- `docs/phase1_6_architecture_summary.md`: completed baseline.
- `docs/agentic_runtime_architecture.md`: long-term agent architecture.
- `docs/phase6_completion_summary.md`: completed Phase 6 details.
- `docs/future_phase_plan.md`: Phase 7-10 execution plan.
- `docs/world_bible.md`: readable world overview.
- `docs/canon/`: retrievable canon corpus.
- `docs/progression_design.md`: Phase 8 mechanics direction.

## Historical Or Compatibility Documents

These are still useful, but should not override the current baseline:

- `docs/phase2_api_plan.md`: Phase 2 planning history.
- `docs/phase4_llm_runtime_plan.md`: Phase 4 structured runtime history.
- `docs/phase5_agentic_runtime_plan.md`: Phase 5 build history.
- `docs/phase6_world_memory_plan.md`: Phase 6 build history.
- `docs/system_design.md`: broad phase-by-phase learning notes.
- `docs/technical_roadmap.md`: long-term technology notes.
- `llm_runtime/`: structured LLM runtime bridge and tests.
- `docs/rag_seed_cards.md`: compact fallback cards used when canon retrieval is unavailable.

## Cleanup Decision

`docs/refactor_plan.md` has been folded into this summary and the Agentic Runtime
architecture. Keeping it as a separate direction document would make the project
harder to navigate, so it should be removed after this consolidation.

No runtime code should be deleted just because it is not the primary path. Phase
4 modules and fallback docs still protect tests, compatibility, and learning.

## Phase 7 Readiness

Phase 7 should start from this baseline:

- Agentic Runtime is the primary world-mode path.
- Phase 1 tutorial behavior remains available.
- RAG and memory exist, but are not final-quality yet.
- Location continuity has a first implementation through `current_scene_focus`.
- The next problem is playability: speed, opening, story quality, dice display,
  and repeatable playtests.
