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
The rule system confirms reality.
Only validated structured state becomes game truth.
```

## Current State

Current implementation:

- Phase 1: Python CLI core.
- Phase 2: FastAPI service layer.
- Current milestone: Phase 2 Complete.
- Existing reusable core lives in `phase1_cli/`.
- Existing API layer lives in `phase2_api/`.

Current important files:

- `phase1_cli/main.py`: CLI entry point.
- `phase1_cli/game_service.py`: player input orchestration and `GameResponse`.
- `phase1_cli/rule_engine.py`: deterministic game rules.
- `phase1_cli/story.py`: fixed text rendering.
- `phase1_cli/game_state.py`: mutable game state.
- `phase1_cli/character.py`: character model and creation.
- `phase1_cli/save_manager.py`: local JSON save/load.
- `phase2_api/main.py`: FastAPI app entry point.
- `phase2_api/routes/`: API route modules.
- `phase2_api/services/session_store.py`: in-memory game sessions.
- `docs/world_bible.md`: world canon.
- `docs/llm_runtime_design.md`: LLM runtime and validation rules.
- `docs/phase2_api_plan.md`: FastAPI migration plan.
- `docs/system_design.md`: phase-by-phase architecture and data flow.
- `docs/technical_roadmap.md`: long-term technology stack and adoption order.

Some target modules do not exist yet. Do not create future modules unless the current task explicitly asks for that phase or feature.

## Target Architecture

The long-term architecture should move toward this shape:

```text
phase1_cli/
  CLI entry point and reusable rule-driven game core.

phase2_api/
  FastAPI routes, request/response schemas, and API session handling.

llm_runtime/
  Specialized LLM agents for intent parsing, narration, scene generation, event generation, NPC dialogue, and memory summarization.

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
- LLM layers must not directly mutate `GameState`.
- All LLM-generated proposals must be validated before they become persistent world facts.
- RAG documents provide canon context, but rule modules still decide state changes.
- Do not let LLM-generated text add HP, SAN, money, clues, items, locations, factions, or endings unless the deterministic rule result already contains them.
- World canon belongs in `docs/world_bible.md`.
- LLM runtime rules belong in `docs/llm_runtime_design.md`.
- Do not put world canon into AGENTS.md. AGENTS.md is for engineering rules.

## Multi-Agent Direction

The long-term LLM layer may use multiple specialized agents, but only after API, state, validator, and memory boundaries are stable.

Possible specialized agents:

- Intent Parser Agent: converts natural-language input into structured action candidates.
- Scene Generator Agent: proposes local scenes and environmental details.
- Event Generator Agent: proposes side events and travel events.
- NPC Dialogue Agent: generates dialogue using only NPC-visible knowledge.
- Narrator Agent: turns validated rule results into atmospheric text.
- Memory Summarizer Agent: summarizes committed events without adding new facts.
- Validator Agent or deterministic validator: checks proposals against world canon and state rules.

Rules:

- Agents may propose, but cannot commit state.
- Agents must not directly mutate `GameState`.
- Agents must not grant HP, SAN, money, clues, items, locations, factions, or endings.
- All agent proposals must pass validation before becoming persistent facts.
- Start with explicit Python functions before introducing a multi-agent framework.

## Documentation Rules

- When gameplay behavior changes, update `README.md` and `CHANGELOG.md`.
- When world canon changes, update `docs/world_bible.md`.
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

## Phase 2 Direction

Phase 2 service-layer rules:

- Keep the separate `phase2_api/` package.
- Use FastAPI and Pydantic.
- Keep `phase1_cli/` reusable instead of copying logic.
- Start with in-memory game sessions before adding a database.
- Current Phase 2 endpoints:
  - `GET /health`
  - `GET /classes`
  - `GET /gods`
  - `GET /locations`
  - `POST /characters`
  - `POST /games`
  - `GET /games`
  - `GET /games/{game_id}`
  - `DELETE /games/{game_id}`
  - `POST /games/{game_id}/actions`

Phase 2 should stop at API/service/session-management readiness. It should not add LLM, RAG, database persistence, web UI, Docker, or user accounts unless explicitly requested.
