# AGENTS.md

## Project Vision

Pantheon Age is a rule-driven LLM Agent text adventure framework set in a Victorian occult world governed by a fixed pantheon.

The final project should support:

- deterministic game rules;
- natural-language player actions;
- structured game state;
- FastAPI service endpoints;
- persistent world memory;
- RAG-backed world canon;
- agent orchestration;
- multi-agent collaboration for specialized LLM roles;
- tool registry and permission boundaries;
- tracing, evals, and observability;
- prompt and policy management;
- performance and speed optimization;
- constrained LLM narration, scene generation, event generation, and NPC dialogue;
- eventually a web UI.

Core principle:

```text
LLM creates possibilities.
Rules constrain authority, not imagination.
The rule system confirms reality.
Only validated structured state becomes game truth.
```

The rule system exists to compensate for LLM weaknesses such as context drift,
inconsistent adjudication, weak long-term planning, and unreliable memory. It
must not become a ceiling on LLM creativity.

## Current State

Current implementation:

- Phase 1: Python CLI core.
- Phase 2: FastAPI service layer.
- Phase 3: SQLite persistence complete.
- Phase 4: structured LLM proposal runtime with optional OpenAI provider.
- Phase 5: Agentic Runtime baseline complete.
- Current milestone: Phase 5 final integration complete.
- Next milestone: Phase 6 World Knowledge And Persistent Memory.
- Existing reusable core lives in `phase1_cli/`.
- Existing API layer lives in `phase2_api/`.
- Existing persistence layer lives in `phase3_persistence/`.
- Existing LLM runtime contracts live in `llm_runtime/`.
- Existing Agentic Runtime baseline lives in `agentic_runtime/`.

Current important files:

- `phase1_cli/main.py`: CLI entry point.
- `phase1_cli/game_service.py`: player input orchestration and `GameResponse`.
- `phase1_cli/rule_engine.py`: deterministic game rules.
- `phase1_cli/story.py`: fixed text rendering.
- `phase1_cli/game_state.py`: mutable game state.
- `phase1_cli/character.py`: character model and creation.
- `phase1_cli/save_manager.py`: local JSON save/load.
- `phase1_cli/scenarios.py`: tutorial/world-mode scenario helpers and game-mode flags.
- `phase2_api/main.py`: FastAPI app entry point.
- `phase2_api/routes/`: API route modules.
- `phase2_api/services/session_store.py`: API session service.
- `phase3_persistence/config.py`: persistence configuration.
- `phase3_persistence/errors.py`: persistence-layer errors.
- `phase3_persistence/sqlite_repository.py`: SQLite game session and event repository.
- `agentic_runtime/contracts.py`: Phase 5 proposal/result contracts.
- `agentic_runtime/orchestrator.py`: minimal Agentic Runtime turn orchestration.
- `agentic_runtime/providers.py`: Phase 5 provider interfaces, local providers, default optional OpenAI Turn Director provider, optional legacy OpenAI Intent/RuleArbiter/WorldBundle providers, and optional full OpenAI NPC/Event/Item/Narrator providers.
- `agentic_runtime/intent_agent.py`: local Intent Agent baseline.
- `agentic_runtime/rule_arbiter_agent.py`: local Rule Arbiter Agent baseline.
- `agentic_runtime/scene_agent.py`: temporary scene proposal baseline.
- `agentic_runtime/npc_agent.py`: temporary NPC proposal baseline.
- `agentic_runtime/event_agent.py`: temporary event proposal baseline.
- `agentic_runtime/item_agent.py`: temporary item proposal baseline.
- `agentic_runtime/state_commit.py`: commit layer that writes validated rule results.
- `agentic_runtime/memory_retriever.py`: local memory retrieval baseline.
- `agentic_runtime/memory_curator.py`: local Memory Curator baseline.
- `agentic_runtime/memory_store.py`: local validated memory record store.
- `agentic_runtime/world_slice.py`: world-mode city/origin/visible-memory slice helpers.
- `agentic_runtime/narrator_agent.py`: local Narrator Agent baseline.
- `agentic_runtime/validators.py`: Phase 5 validators.
- `agentic_runtime/world_relations.py`: dynamic nation relation signal and snapshot interface.
- `llm_runtime/contracts.py`: structured LLM proposal/result contracts.
- `llm_runtime/actions.py`: structured action candidate validation and fallback.
- `llm_runtime/adjudication.py`: generic adjudication requests from semantic action candidates.
- `llm_runtime/proposals.py`: scene/event proposal validation and authority checks.
- `llm_runtime/narrator.py`: safe narration proposal validation and fallback.
- `llm_runtime/providers.py`: action/narration provider interfaces, local fallback providers, and optional OpenAI providers.
- `llm_runtime/prompts.py`: prompt loading helpers.
- `prompts/action_candidate.md`: Action Candidate prompt and policy file.
- `prompts/open_generation.md`: Open Generation prompt and policy file.
- `prompts/scene_event.md`: Scene/Event proposal prompt and policy file.
- `prompts/narrator.md`: Narrator prompt and policy file.
- `docs/world_bible.md`: world canon.
- `docs/rag_seed_cards.md`: compact RAG cards for gods, classes, and countries.
- `docs/tone_guide.md`: original tone guide for narration and generation.
- `docs/forbidden_outputs.md`: LLM forbidden outputs and authority boundaries.
- `docs/inspiration_notes.md`: high-level inspirations and originality boundaries.
- `docs/progression_design.md`: progression, attributes, class levels, faith levels, rituals, items, and costs.
- `docs/llm_runtime_design.md`: LLM runtime and validation rules.
- `docs/live_llm_testing.md`: safe local `.env` setup for real LLM smoke/live tests.
- `docs/phase2_api_plan.md`: FastAPI migration plan.
- `docs/phase4_llm_runtime_plan.md`: Phase 4 LLM runtime implementation plan.
- `docs/phase5_agentic_runtime_plan.md`: Phase 5 Agentic Runtime staged implementation plan.
- `docs/phase5_completion_summary.md`: Phase 5 final integration summary.
- `docs/future_phase_plan.md`: execution-oriented Phase 6+ roadmap.
- `docs/agentic_runtime_architecture.md`: long-term multi-agent runtime architecture.
- `docs/refactor_plan.md`: corrected direction for creative LLM generation and rule authority.
- `docs/system_design.md`: phase-by-phase architecture and data flow.
- `docs/technical_roadmap.md`: long-term technology stack and adoption order.

Some target modules do not exist yet. Do not create future modules unless the current task explicitly asks for that phase or feature.

## Open Generation Principle

Do not hard-code every concrete location, item, NPC, relationship, team,
organization, route, rumor, or event.

LLM layers should be allowed to freely propose concrete content within world
constraints. The program exists to compensate for LLM weaknesses:

- context drift;
- inconsistent logic;
- unreliable long-term memory;
- weak planning;
- tendency to turn player speculation into fact;
- tendency to grant unearned rewards or reveal hidden truth.

Therefore code should focus on authority levels, validators, rule adjudication,
memory commit boundaries, persistence rules, forbidden outputs, and deterministic
mechanical results.

The program should not become a list of every possible room, item, NPC, team,
relationship, organization, or event.

## Target Architecture

The long-term architecture should move toward this shape:

```text
phase1_cli/
  CLI entry point and reusable rule-driven game core.

phase2_api/
  FastAPI routes, request/response schemas, and API session handling.

phase3_persistence/
  SQLite repository, database path configuration, persistence errors, and future persistence abstractions.

llm_runtime/
  Current Phase 4 LLM provider and proposal runtime.

agentic_runtime/
  Future multi-agent orchestration for intent, scene, NPC, event, rule arbitration, memory curation, state commit, and narration.

validation/
  Validators for LLM proposals, world canon, rewards, hidden information, and state mutation permissions.

memory/
  Persistent player history, generated facts, NPC relationships, faction state, and save-backed world changes.

rag/
  Retrieval over world canon, country docs, deity docs, class docs, tone guides, and forbidden-output rules.

observability/
  Tracing, token usage, LLM call logs, latency metrics, and debugging records.

evals/
  Agent behavior tests, prompt-injection cases, proposal fixtures, and narrative safety checks.

prompts/
  Versioned prompts and policy text for LLM roles.

tools/
  Tool registry and permission-checked agent tools.

web_ui/
  Future web interface.
```

Do not scaffold all of this at once. Build one small, verifiable layer at a time.

## Architecture Boundaries

- CLI-specific code belongs only in `phase1_cli/main.py`.
- Reusable game logic belongs in `phase1_cli/rule_engine.py`, `phase1_cli/game_service.py`, `phase1_cli/story.py`, and related model modules.
- API route code should belong only in `phase2_api/`.
- Do not move reusable game logic into CLI or API files.
- Do not let CLI, API, story, or LLM layers directly mutate `GameState`.
- If shared behavior is needed by both CLI and API, put it in the service or rule layer first.
- Future FastAPI code should call `phase1_cli.game_service.handle_player_input()`.
- Keep `main.py` thin. It should only handle CLI input/output, printing, and local save/load.
- Long-term Agentic Runtime design belongs in `docs/agentic_runtime_architecture.md`.
- Do not keep expanding `ActionCandidate` with one-off keyword or intent patches when the real issue belongs to Phase 5 open action understanding.

## Runtime Truth Rules

- Player input is not world truth. It is intent, action, or speculation.
- LLM output is not world truth. It is proposal, narration, or candidate content.
- `rule_engine.py` decides state changes, rolls, HP, SAN, clues, items, movement, and endings.
- Important state changes must be represented as structured data.
- Narration must obey deterministic rule results.
- If `rule_result` does not grant a clue, item, location change, death, faction change, or ending, narration must not claim it happened.
- LLM-generated content becomes persistent only after validation and an explicit commit to game state or memory.

## API / Service Compatibility

- Do not change the public signature or return shape of `handle_player_input()` unless the task explicitly requires it.
- If a public service interface changes, update all callers, tests, README examples, and CHANGELOG entries.
- Prefer adding small helper functions over rewriting the service layer.
- `GameResponse.to_dict()`, `GameState.to_public_dict()`, and `Character.to_public_dict()` are API-facing shapes and should stay stable unless a task explicitly changes them.

## Randomness

- Random rolls must be handled inside `rule_engine.py` or a dedicated deterministic helper.
- Random behavior should be seedable or testable.
- Do not call `random` directly from CLI, API, story, or LLM-related modules.
- Tests should avoid flaky randomness.

## Performance Rules

- Do not optimize before measuring.
- Keep route handlers thin and move reusable work into services.
- Cache static world/config data when it becomes a repeated cost.
- Avoid sending full chat history or full world canon to LLM calls.
- Track latency, token usage, and cost once LLM calls exist.
- Prefer simple, readable code until profiling shows a real bottleneck.

## LLM / RAG Runtime Boundaries

- LLM layers may propose narration, scene details, NPC dialogue, or structured action candidates.
- Long-term agents may also propose rule adjudication, memory curation, generated NPCs, generated locations, generated events, generated items, and final narration.
- LLM layers must not directly mutate `GameState`.
- All LLM-generated proposals must be validated before they become persistent world facts.
- RAG documents provide canon context, but rule modules still decide state changes.
- Rules constrain authority, not imagination. Prefer generic adjudication, authority levels, and permission boundaries over hard-coding every possible story action.
- LLM-generated content should be classified by authority level: flavor, temporary, persistent, mechanical, or secret.
- Do not let LLM-generated text add HP, SAN, money, clues, items, locations, factions, or endings unless the deterministic rule result already contains them.
- World canon belongs in `docs/world_bible.md`.
- Compact RAG seed cards belong in `docs/rag_seed_cards.md`.
- Tone and atmosphere guidance belongs in `docs/tone_guide.md`.
- Forbidden LLM behavior belongs in `docs/forbidden_outputs.md`.
- High-level inspiration notes belong in `docs/inspiration_notes.md`.
- Progression, attributes, class levels, faith levels, ritual ascension, items, and costs belong in `docs/progression_design.md`.
- LLM runtime rules belong in `docs/llm_runtime_design.md`.
- Do not put world canon into AGENTS.md. AGENTS.md is for engineering rules.
- Do not use copyrighted full novels as RAG corpus. Use original project canon, user-written notes, and high-level inspiration summaries only.
- Program boundaries should compensate for LLM weaknesses without becoming a ceiling on creative generation.

## Multi-Agent Direction

The long-term LLM layer may use multiple specialized agents, but only after API, state, validator, and memory boundaries are stable.

Possible specialized agents:

- Intent Parser Agent: converts natural-language input into structured action candidates.
- Rule Arbiter Agent: proposes rule adjudication, checks, risks, costs, allowed effects, and denied effects.
- Scene Generator Agent: proposes local scenes and environmental details.
- Event Generator Agent: proposes side events and travel events.
- NPC Agent: proposes NPCs, visible knowledge, dialogue, attitude, and short-term goals.
- Item Agent: proposes temporary items, objects, materials, and usage risks.
- NPC Dialogue Agent: generates dialogue using only NPC-visible knowledge.
- Memory Retriever: retrieves relevant current memory before agent calls.
- Memory Curator Agent: decides what to store, discard, compress, retrieve, or keep hidden.
- Narrator Agent: turns validated rule results into atmospheric text.
- Memory Summarizer Agent: summarizes committed events without adding new facts.
- Validator Agent or deterministic validator: checks proposals against world canon and state rules.

Rules:

- Agents may propose, but cannot commit state.
- Agents must not directly mutate `GameState`.
- Agents must not grant HP, SAN, money, clues, items, locations, factions, or endings.
- Agents should expand possible scenes, NPCs, events, and actions within validated authority boundaries.
- All agent proposals must pass validation before becoming persistent facts.
- Start with explicit Python functions before introducing a multi-agent framework.

## Documentation Rules

- When gameplay behavior changes, update `README.md` and `CHANGELOG.md`.
- When world canon changes, update `docs/world_bible.md`.
- When compact RAG cards change, update `docs/rag_seed_cards.md`.
- When tone direction changes, update `docs/tone_guide.md`.
- When forbidden outputs or originality boundaries change, update `docs/forbidden_outputs.md` or `docs/inspiration_notes.md`.
- When progression, attributes, class levels, faith levels, ritual ascension, items, or costs change, update `docs/progression_design.md`.
- When LLM, RAG, validation, or memory behavior changes, update `docs/llm_runtime_design.md`.
- When API design changes, update `docs/phase2_api_plan.md` or the relevant API docs.
- When architecture, module boundaries, or data flow changes, update `docs/system_design.md`.
- When long-term technology choices, agent engineering capabilities, performance strategy, or adoption order changes, update `docs/technical_roadmap.md`.
- Do not mix world canon, implementation notes, and runtime rules in the same document.

## Development Workflow

Before large edits:

1. Read the relevant files first.
2. Explain the plan briefly.
3. Keep changes scoped.
4. Add or update tests when behavior changes.
5. Run verification commands before summarizing.

For small explanations or tiny text edits, a full plan is not required.

Prefer small, verifiable iterations over large rewrites.

## Verification

Use these commands from the project root:

```bash
./.venv/bin/python -m py_compile phase1_cli/*.py tests/*.py
./.venv/bin/python -m py_compile phase2_api/*.py phase2_api/routes/*.py phase2_api/services/*.py
./.venv/bin/python -m py_compile phase3_persistence/*.py
./.venv/bin/python -m py_compile llm_runtime/*.py
./.venv/bin/python -m py_compile agentic_runtime/*.py
./.venv/bin/python -m unittest discover -s tests
```

The preferred CLI launch command is:

```bash
./.venv/bin/python -m phase1_cli.main
```

The preferred API launch command is:

```bash
./.venv/bin/uvicorn phase2_api.main:app --reload
```

## Git Rules

- Do not commit, push, or create git tags unless the user explicitly asks.
- When Git changes are ready, provide the exact commands for the user to run.
- Do not revert unrelated user changes.
- Preserve local save files and virtual environments as ignored local data.

## Communication Rules

- When explaining code to the user, use clear, easy-to-understand Chinese and connect concepts to the current project.
- The user is learning while building, so explain why architecture choices matter.
- Keep summaries practical: what changed, why it matters, how to verify.

## General Constraints

- Do not add new dependencies unless the task clearly requires them.
- Do not mix CLI `input()` / `print()` logic into reusable service, rule, API, or LLM modules.
- Do not skip tests after behavior changes.
- Do not rewrite unrelated files.
- Preserve the project as a resume-friendly AI Agent engineering project.

## Phase 2 / Phase 3 Direction

Phase 2 service layer is complete.

- Keep the separate `phase2_api/` package.
- Use FastAPI and Pydantic.
- Keep `phase1_cli/` reusable instead of copying logic.
- Current API endpoints:
  - `GET /health`
  - `GET /classes`
  - `GET /gods`
  - `GET /locations`
  - `POST /characters`
  - `POST /games`
  - `GET /games`
  - `GET /games/{game_id}`
  - `GET /games/{game_id}/events`
  - `DELETE /games/{game_id}`
  - `POST /games/{game_id}/actions`

Phase 3 persistence rules:

- Keep `phase3_persistence/` separate from route modules.
- Use SQLite through the standard library for the local persistence layer.
- Support `PANTHEON_DB_PATH` for local database path configuration.
- Keep route shapes stable while replacing storage internals.
- Persist validated, versioned `GameState.to_dict()` snapshots only.
- Persist committed event logs as ordered event rows.
- Do not store raw LLM output as truth.
- Do not add PostgreSQL, SQLAlchemy, Alembic, LLM, RAG, web UI, Docker, or user accounts unless explicitly requested.

Phase 4 LLM runtime contract rules:

- Keep `llm_runtime/` separate from CLI, API, rule, and persistence modules.
- Start with structured proposal contracts before real model calls.
- Use provider interfaces so model calls can be swapped without changing rule logic.
- `TemplateNarrationProvider` must work without API keys or network access.
- `OpenAIActionCandidateProvider` and `OpenAINarrationProvider` are optional real model providers.
- Real LLM calls must be enabled through environment variables and must always keep local fallback behavior.
- Use `PANTHEON_USE_LLM=1` plus `OPENAI_API_KEY` to enable OpenAI providers.
- Use `PANTHEON_OPENAI_MODEL` to override the default model.
- Use `PANTHEON_SHOW_RUNTIME=1` to show Phase 4 runtime summaries in CLI.
- Prefer local `.env` configuration for live LLM testing. Do not ask the user to paste API keys into chat.
- Do not read, print, summarize, or commit `.env`.
- Use `.env.example` as the committed template for local secrets.
- If a task touches provider behavior or live LLM behavior and `.env` is configured, run `./.venv/bin/python -m llm_runtime.smoke_test`.
- Run `./.venv/bin/python -m unittest tests.test_live_openai_provider` only when live tests are explicitly enabled by `PANTHEON_RUN_LIVE_LLM_TESTS=1`.
- Future local model deployment should be added as a provider-compatible backend, not as a separate rule path.
- Candidate local runtimes include Ollama, LM Studio, and vLLM through an OpenAI-compatible local endpoint.
- Local model providers must pass the same validators and fallback rules as OpenAI providers.
- Keep prompts and policy text in `prompts/`, not scattered through provider code.
- Prompt loaders must not allow path traversal.
- Narration proposals may claim only facts already approved by `rule_result`.
- Invalid proposals must fall back to deterministic story text.
- Do not require API keys or network calls in tests.
- Do not let `llm_runtime/` mutate `GameState`.

Phase 5 Agentic Runtime rules:

- Keep `agentic_runtime/` separate from `llm_runtime/`; Phase 5 orchestrates agents, Phase 4 provides older LLM proposal providers.
- Enable the current Phase 5 CLI path with `PANTHEON_USE_AGENTIC_RUNTIME=1`.
- Enable Phase 5 OpenAI-backed Agentic Runtime with `PANTHEON_USE_AGENTIC_LLM=1`; this is separate from Phase 4 `PANTHEON_USE_LLM`.
- Keep `PANTHEON_AGENTIC_TURN_DIRECTOR=1` for normal low-latency live play. This uses one OpenAI Turn Director call to propose intent, adjudication, scene, NPC, event, item, and compact narration.
- Set `PANTHEON_AGENTIC_TURN_DIRECTOR=0` only when debugging the older multi-call Intent/RuleArbiter/WorldBundle path.
- Enable slower full-agent NPC/Event/Item/Narrator OpenAI calls only with `PANTHEON_AGENTIC_FULL_LLM=1`.
- `PANTHEON_GAME_MODE=world` starts the CLI in Phase 5 world-mode; tutorial remains the default fixed Mist Abbey scenario.
- World-mode character creation currently allows eight important countries as origin countries: the five great powers, Noctia, Selemia, and Rosvia.
- Store origin country, identity, and starting city on `Character.flags` so Agentic Runtime and future API/UI layers can use them.
- `PANTHEON_USE_AGENTIC_LLM=1` normally uses OpenAI Turn Director; the program still validates adjudication, rolls dice, commits state, and falls back if proposals fail validation.
- Memory Retriever, Memory Curator, and State Commit remain local providers in the Phase 5 baseline.
- Intent Agent must preserve open player method, goals, targets, and assumptions.
- Rule Arbiter Agent may propose adjudication, but it cannot directly mutate state.
- State Commit Layer is the only Phase 5 layer that writes game reality, and it currently delegates to the deterministic `rule_engine`.
- Memory Curator Agent proposes memory candidates; validated persistent candidates are stored through the local memory store.
- NPC/Event/Item Agents may generate temporary candidates only; they must not grant clues, inventory changes, state changes, or persistent facts.
- Do not solve Phase 5 natural-language issues by patching Phase 1 keyword lists unless the task is explicitly about the tutorial parser.
- Phase 5 stage-gated work is complete as of `v5.8.0`.
- Do not start Phase 6 unless the user explicitly asks for Phase 6 planning or development.
