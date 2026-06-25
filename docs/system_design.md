# Pantheon Age System Design

This document records how the project is structured at each phase and how data
flows through the system. It is intentionally simple and should grow one phase
at a time.

## Core Principle

```text
LLM creates possibilities.
Rules constrain authority, not imagination.
The rule system confirms reality.
Only validated structured state becomes game truth.
```

In Chinese:

```text
LLM 负责提出可能性。
规则限制的是改变现实的权限，而不是想象力。
规则系统负责裁定现实。
只有通过验证的结构化状态，才算真正发生。
```

The rule engine should stabilize LLM creativity. It should not become a list of
all possible scenes.

## Phase 1: CLI Rule Engine

Phase 1 is a local command-line game.

### Data Flow

```text
player input
  -> phase1_cli/main.py
  -> phase1_cli/game_service.py
  -> phase1_cli/intent_parser.py
  -> phase1_cli/rule_engine.py
  -> phase1_cli/game_state.py
  -> phase1_cli/story.py
  -> terminal output
```

### Module Responsibilities

- `main.py`: reads terminal input, prints terminal output, handles local save/load.
- `game_service.py`: receives player text and returns a structured `GameResponse`.
- `intent_parser.py`: converts natural-language-like input into an intent dict.
- `rule_engine.py`: applies deterministic rules and changes game state.
- `game_state.py`: stores the current mutable state of one play session.
- `story.py`: renders rule results into readable text.
- `save_manager.py`: saves and loads local JSON files for the CLI.

### Why This Design

The CLI version proves the game loop before adding API, database, frontend, or
LLM complexity.

The most important boundary is:

```text
main.py handles input/output.
rule_engine.py decides state changes.
```

## Phase 2: FastAPI Service Layer

Phase 2 exposes the Phase 1 core as a REST API.

Status: completed in `v2.1.0`.

### Data Flow

```text
HTTP JSON request
  -> phase2_api/routes/*.py
  -> phase2_api/schemas.py
  -> phase2_api/services/session_store.py
  -> phase1_cli/game_service.py
  -> phase1_cli/rule_engine.py
  -> GameState
  -> HTTP JSON response
```

### API Layer Responsibilities

- `phase2_api/main.py`: creates the FastAPI app and includes route modules.
- `phase2_api/routes/`: defines HTTP endpoints.
- `phase2_api/schemas.py`: defines request and response shapes with Pydantic.
- `phase2_api/services/session_store.py`: stores temporary sessions in Phase 2 and delegates to persistence in Phase 3.

### Current Endpoints

```text
GET    /health
GET    /classes
GET    /gods
GET    /locations
POST   /characters
POST   /games
GET    /games
GET    /games/{game_id}
GET    /games/{game_id}/events
DELETE /games/{game_id}
POST   /games/{game_id}/actions
```

### Game Session Flow

Creating a game:

```text
POST /games
  -> validate character request
  -> build Character
  -> create GameState
  -> generate game_id
  -> store game_id -> GameState
  -> return opening_text and public state
```

Submitting an action:

```text
POST /games/{game_id}/actions
  -> find GameState by game_id
  -> call handle_player_input(state, text)
  -> rule_engine mutates GameState if needed
  -> return GameResponse as JSON
```

Listing and deleting sessions:

```text
GET /games
  -> return summaries of active sessions

DELETE /games/{game_id}
  -> remove one session
```

### Phase 2 Limitations

- Sessions are stored in memory only.
- Service restart deletes all API sessions.
- There is no database yet.
- There are no user accounts yet.
- There is no LLM, RAG, or web UI yet.

These limitations are intentional. Phase 2 focuses on a clean API boundary
before Phase 3 persistence.

## Phase 3: Persistence And Memory

Current status: `v3.1.0 Phase 3 Persistence Complete`.

Phase 3 replaces in-memory-only API sessions with durable SQLite persistence.

### Current Data Flow

```text
HTTP JSON request
  -> phase2_api/routes/*.py
  -> phase2_api/schemas.py
  -> phase2_api/services/session_store.py
  -> phase3_persistence/sqlite_repository.py
  -> SQLite database
  -> phase1_cli/game_service.py
  -> phase1_cli/rule_engine.py
  -> versioned GameState JSON snapshot
  -> ordered event rows
  -> HTTP JSON response
```

### Persistence Layer

```text
phase3_persistence/
  config.py
  errors.py
  sqlite_repository.py
```

Default database path:

```text
data/pantheon_age.sqlite3
```

This can be overridden with:

```text
PANTHEON_DB_PATH
```

### Current SQLite Tables

```text
game_sessions
  game_id TEXT PRIMARY KEY
  state_json TEXT NOT NULL
  created_at TEXT NOT NULL
  updated_at TEXT NOT NULL

game_events
  game_id TEXT NOT NULL
  event_index INTEGER NOT NULL
  text TEXT NOT NULL
  created_at TEXT NOT NULL
```

### What Phase 3 Adds

- SQLite-backed API game sessions;
- versioned JSON snapshots using `GameState.to_dict()`;
- compatibility with old plain `GameState` JSON snapshots;
- rebuild through `GameState.from_dict()`;
- save on game creation;
- save after player actions;
- ordered event log rows;
- `GET /games/{game_id}/events`;
- configurable database path through `PANTHEON_DB_PATH`;
- persistence-layer errors translated into API errors;
- list, read, and delete sessions through the repository;
- repository-level tests with temporary SQLite databases.

### Storage Boundary

```text
Routes do not talk to SQLite directly.
session_store.py talks to the repository.
repository saves validated GameState snapshots.
repository also mirrors committed event logs into game_events.
```

The core API route shape remains stable. Phase 3 adds one read-only event
endpoint for inspecting persisted game history.

### What Phase 3 Should Still Avoid

- LLM runtime;
- RAG;
- multi-agent orchestration;
- frontend UI;
- user accounts;
- PostgreSQL, SQLAlchemy, and Alembic until this local persistence layer is understood.

## Progression System Design

Current status: design-only.

The long-term growth model is documented in:

```text
docs/progression_design.md
```

The planned model contains:

- class levels for skill growth;
- faith levels for talents, prayers, devotion, and favor;
- ritual ascension for supernatural rank breakthroughs;
- items, relics, ritual media, and cursed objects;
- costs, burdens, oaths, corruption, suspicion, and faction attention;
- a future six-attribute model: Physique, Agility, Insight, Knowledge, Will, Communion.

This should not be implemented as one giant rewrite. It affects:

- `Character`;
- save/load format;
- public API state shape;
- SQLite snapshots;
- rule adjudication;
- LLM proposal validation.

When implementation starts, add the smallest playable slice first and keep old saves compatible.

## Phase 4: Open Generation Proposal Runtime

Current status: `v4.7.0 Phase 4 Real LLM CLI Runtime`.

Phase 4 is complete. It proves the transitional LLM runtime:

- structured proposal contracts;
- OpenAI-backed providers;
- prompt files;
- local validators;
- deterministic fallback;
- CLI integration;
- smoke and live-test hooks.

Phase 4 should not keep expanding the old `ActionCandidate(intent=...)` shape
with one-off keywords, aliases, or intent enum patches. That object is a bridge
from the old CLI loop to the next runtime, not the final interaction model.

Phase 4 started by defining contracts before real model calls, and now includes
optional OpenAI-backed providers. Its final scope is structured proposal
contracts, provider boundaries, prompt files, semantic action candidate
validation, generic adjudication requests, open generation proposal validation,
scene/event proposal validation, real-provider integration, and safe fallback
behavior.

Current RAG-ready documents:

```text
docs/world_bible.md
docs/rag_seed_cards.md
docs/tone_guide.md
docs/forbidden_outputs.md
docs/inspiration_notes.md
```

These documents give future LLM calls canon, compact seed cards, tone direction,
forbidden behavior, and originality boundaries. They are context sources, not
state authority.

### Current Modules

```text
llm_runtime/
  adjudication.py
  actions.py
  contracts.py
  narrator.py
  proposals.py
  providers.py
  prompts.py

prompts/
  action_candidate.md
  narrator.md
  open_generation.md
  scene_event.md
```

### Current Data Flow

```text
player text
  -> ActionCandidateProvider
  -> prompts/action_candidate.md
  -> semantic ActionCandidate
  -> llm_runtime/actions.py
  -> validate supported intent, target rules, item rules, tags, confidence range
  -> rule_engine action dict or keyword parser fallback
  -> llm_runtime/adjudication.py
  -> AdjudicationRequest with check type, stat, difficulty, risks, costs

local context
  -> Scene/Event proposal provider later
  -> prompts/scene_event.md
  -> SceneProposal / EventProposal
  -> llm_runtime/proposals.py
  -> validate authority level and forbidden claims
  -> display-only flavor/temporary content or rejection

open context
  -> Open Generation proposal provider later
  -> prompts/open_generation.md
  -> GeneratedContentProposal
  -> llm_runtime/proposals.py
  -> validate content type, authority level, and forbidden claims
  -> temporary content or rejection

GameResponse
  -> NarrationProvider
  -> prompts/narrator.md
  -> NarrationProposal
  -> llm_runtime/narrator.py
  -> validate against rule_result
  -> NarrationResult
  -> use proposal text or deterministic fallback text
```

### Current Rules

Action candidates are only proposals:

- supported intent only;
- generated targets are allowed as candidate NPCs, objects, rooms, streets,
  districts, or routes;
- generated targets are not canon until a later validator and memory layer
  explicitly commit them;
- generated item targets are allowed as candidate objects;
- item rewards, inventory changes, and item consumption still require deterministic rules;
- confidence must be between 0 and 1;
- `method`, `desired_outcome`, `risk_tags`, `skill_tags`, and `assumptions`
  preserve player imagination without becoming world truth;
- invalid candidates fall back to the deterministic keyword parser.

Generic adjudication requests do not mutate `GameState`. They prepare the next
rule-engine step by translating rich player intent into:

- check type;
- primary stat;
- difficulty;
- possible risks;
- possible costs.

Narration proposals may claim only facts already approved by `rule_result`:

- approved state changes;
- approved new clues;
- approved location after the action.

If a proposal claims anything else, it is rejected and the system falls back to
the deterministic text from Phase 1.

Scene and event proposals may currently use only:

- `flavor`;
- `temporary`.

They cannot commit:

- `persistent` world facts;
- `mechanical` results;
- `secret` information.

Open generation proposals follow the same rule for locations, NPCs, items,
relationships, teams, organizations, rumors, routes, and events. Generated
content can be displayed as `flavor` or `temporary`, but it cannot become canon,
inventory, relationship state, faction state, clue state, or world memory until
a later validator and memory layer explicitly commit it.

### Current Providers

```text
TemplateNarrationProvider
  -> wraps deterministic story text as a safe proposal

KeywordActionCandidateProvider
  -> wraps current keyword parser output as a safe action candidate

OpenAINarrationProvider
  -> optional OpenAI-backed narration proposal provider

OpenAIActionCandidateProvider
  -> optional OpenAI-backed action candidate provider
```

Providers do not mutate `GameState`. They only return structured proposals such
as `ActionCandidate` or `NarrationProposal` for validation.

Real LLM providers are enabled only when both conditions are true:

```text
PANTHEON_USE_LLM=1
OPENAI_API_KEY is present
```

Otherwise the service layer uses keyword/template fallback providers.

### Prompt Boundary

Prompts and policy text live in `prompts/`.

```text
provider code loads prompt text
prompt text defines output shape and forbidden behavior
validator still enforces the rules in Python
```

Prompt text can guide a model, but it is not a security boundary. The Python
validator remains the authority.

### Future LLM Architecture

The real LLM layer should be added only after proposal contracts and validation
boundaries are stable.

The target is not:

```text
fixed rule output -> LLM polish
```

The target is:

```text
LLM proposes possibilities -> validators/rules decide authority
```

### Future Data Flow

```text
player text
  -> RAG retrieves local/canon context
  -> LLM proposes ActionCandidate / SceneProposal / EventProposal
  -> validators check world canon, hidden info, and state permissions
  -> rule_engine adjudicates mechanical authority and consequences
  -> memory layer decides what can persist
  -> RAG retrieves narration context
  -> Narrator Agent generates NarrationProposal
  -> validators check final claims
  -> validated response
```

### Agent Rule

```text
Agents may propose.
Validators and rule_engine decide.
Only validated state is persisted.
```

## Phase 5: Agentic Runtime Baseline

Current status: `v5.8.0 Phase 5 Final Integration`.

Phase 5 should replace the old "LLM fills a narrow action schema" loop with a
small agentic game loop.

The long-term architecture is documented in:

```text
docs/agentic_runtime_architecture.md
```

Phase 5 completion summary:

```text
docs/phase5_completion_summary.md
```

### Current Implemented Modules

```text
agentic_runtime/
  __init__.py
  contracts.py
  event_agent.py
  intent_agent.py
  item_agent.py
  memory_curator.py
  memory_retriever.py
  memory_store.py
  narrator_agent.py
  npc_agent.py
  orchestrator.py
  providers.py
  rule_arbiter_agent.py
  scene_agent.py
  state_commit.py
  validators.py
  world_slice.py
  world_relations.py
```

The tutorial/world-mode split is handled by:

```text
phase1_cli/scenarios.py
```

### Target Phase 5 Flow

```text
player input
  -> Memory Retriever
  -> Intent Agent
  -> Scene / NPC / Event / Item Agents
  -> Rule Arbiter Agent
  -> Validator Layer
  -> State Commit Layer
  -> Memory Curator Agent
  -> Narrator Agent
  -> CLI / API / Web UI
```

### Current Baseline Flow

```text
player input
  -> Memory Retriever
  -> local Intent Agent
  -> local Scene Agent
  -> local NPC Agent
  -> local Event Agent
  -> local Item Agent
  -> local Rule Arbiter Agent
  -> validators
  -> State Commit Layer
  -> phase1_cli.rule_engine.apply_rule()
  -> local Memory Curator Agent
  -> local Narrator Agent
  -> GameResponse.llm_runtime["agentic_runtime"]
```

The baseline is enabled with:

```text
PANTHEON_USE_AGENTIC_RUNTIME=1
```

The optional OpenAI Turn Director fast path is enabled with:

```text
PANTHEON_USE_AGENTIC_LLM=1
PANTHEON_AGENTIC_TURN_DIRECTOR=1
OPENAI_API_KEY=...
```

Current Phase 5 routes the live path through one optional OpenAI Turn Director
call by default. Turn Director proposes open intent, contextual
DC/check/consequence, categorized Scene/NPC/Event/Item content, and compact
narration. Memory, validation, dice rolls, and
Commit stay local for clearer authority boundaries. Set
`PANTHEON_AGENTIC_TURN_DIRECTOR=0` to debug the older multi-call Intent / Rule
Arbiter / WorldBundle path. To route NPC / Event / Item / Narrator agents
through separate OpenAI calls, set `PANTHEON_AGENTIC_FULL_LLM=1`; this is slower
and mainly useful for agent-level debugging.

`v5.5` adds a local memory store. The store writes only validated
`MemoryCandidate` objects with `should_persist=True`, separates records into
player-known, NPC-known, location, quest, and secret buckets, and refuses raw
OpenAI/LLM provider output as persistent truth.

`v5.6` connects that store back into retrieval. Visible player and quest memory
can affect later turns, location memory enriches scene context, and NPC/secret
memory stays in internal hidden context. Hidden context is not included in the
default serialized runtime payload or public game state.

`v5.7` adds a visible CLI world-mode slice. Local agents generate temporary
scene, NPC, event, and item content from city/origin/visible-memory context, and
the narrator renders a distinct world-slice response while preserving the rule
boundary: no automatic clues, inventory, location changes, faction changes, or
progression rewards.

`v5.3` adds:

```text
PANTHEON_GAME_MODE=world
```

Tutorial mode remains the fixed Mist Abbey scenario. World mode starts from
one of eight important countries, automatically uses Phase 5 Agentic Runtime, and
commits open player actions as `world_action` records instead of forcing them
into the tutorial map.

World-mode character creation currently stores:

```text
origin_country_id
origin_country
origin_country_formal_name
origin_identity
origin_ethnicity
origin_city
origin_church_context
```

This origin data flows into public player state and Agentic Runtime memory
retrieval, so future agents can reason from the player's nationality, ethnicity,
starting city, and local church legality.

Nation-to-nation relations are not fixed canon. They should be modeled as
dynamic world state through:

```text
NationRelationSignal
NationRelationSnapshot
```

Future agents may propose relation signals from politics, factions, religion,
rulers, trade, wars, scandals, and player actions. Program validation and memory
commit decide whether those signals become persistent world state.

Default CLI behavior remains unchanged when this flag is not enabled.

### Phase 5 Responsibilities

- Intent Agent preserves open player intent instead of forcing it into a fixed
  button-like intent too early.
- Scene, NPC, Event, and Item Agents generate temporary possibilities.
- NPC, Event, and Item proposals are validated as temporary content and cannot
  claim clues, inventory changes, state changes, or persistent facts.
- Rule Arbiter Agent proposes checks, risks, costs, allowed effects, and denied
  effects.
- Validators approve or reject proposals.
- State Commit Layer is the only layer that writes game reality.
- Memory Curator Agent decides what to store, discard, compress, retrieve, or
  keep hidden.
- Narrator Agent writes final text from confirmed results only.

### Phase 5 Boundary

```text
LLM creates possibilities.
Agents organize and reason over them.
Programs validate, commit, remember, and audit.
```

Phase 5 is complete as a baseline. The completed slice runs in CLI, supports
world-mode, keeps tutorial compatibility, uses fake providers in ordinary tests,
and can optionally call live LLM providers through explicit environment flags.

The agentic boundary is proven in both tutorial and world-mode paths. For
example, `跳向前厅` is preserved as an open player method, then the Rule Arbiter
bridges it to a deterministic `move` action because `前厅` is reachable from the
current location. In world-mode, open actions generate temporary scene, NPC,
event, and item content while validated memory records can flow into later
turns. This does not add `跳向` as a Phase 1 keyword.

### Content Authority Levels

```text
flavor
  Free atmosphere and sensory detail.

temporary
  Local scene details, minor rumors, unnamed NPCs.

persistent
  Named NPCs, relationships, local facts, city events.

mechanical
  HP, SAN, items, clues, location, factions, endings.

secret
  Hidden truth and unrevealed core mysteries.
```

LLM may generate all of these as proposals, but only validators, rules, and
memory can decide what authority each proposal receives.

## Design Review Checklist

Before adding a new feature, ask:

1. Is this CLI-only, API-only, or reusable game logic?
2. Does it change game truth?
3. Should this live in route, schema, service, rule engine, or repository?
4. Does it need a test?
5. Does it require README, CHANGELOG, or design doc updates?

If a feature changes durable state or public API shape, update this document.
