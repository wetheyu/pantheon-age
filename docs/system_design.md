# Pantheon Age System Design

This document records how the project is structured at each phase and how data
flows through the system. It is intentionally simple and should grow one phase
at a time.

## Core Principle

```text
LLM creates possibilities.
The rule system confirms reality.
Only validated structured state becomes game truth.
```

In Chinese:

```text
LLM 负责提出可能性。
规则系统负责裁定现实。
只有通过验证的结构化状态，才算真正发生。
```

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

Current status: `v2.1.0 Phase 2 Complete`.

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
- `phase2_api/services/session_store.py`: stores temporary in-memory game sessions.

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
  -> store game_id -> GameState in memory
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
  -> return summaries of active in-memory sessions

DELETE /games/{game_id}
  -> remove one in-memory session
```

### Current Limitations

- Sessions are stored in memory only.
- Service restart deletes all API sessions.
- There is no database yet.
- There are no user accounts yet.
- There is no LLM, RAG, or web UI yet.

These limitations are intentional. Phase 2 focuses on a clean API boundary
before Phase 3 persistence.

## Phase 3: Persistence And Memory

Phase 3 should replace in-memory-only API sessions with durable persistence.

### Target Data Flow

```text
HTTP request
  -> route
  -> schema
  -> service
  -> repository
  -> database
  -> service
  -> response
```

### New Layer

```text
repositories/
  game_repository.py
  character_repository.py
  event_log_repository.py
```

Or a similar structure under the future persistence package.

### What Phase 3 Should Add

- database-backed game sessions;
- durable character state;
- durable event log;
- save/load through API instead of local CLI JSON only;
- migration scripts;
- tests for persistence round trips.

### What Phase 3 Should Still Avoid

- LLM runtime;
- RAG;
- multi-agent orchestration;
- frontend UI;
- user accounts unless explicitly chosen as the persistence scope.

## Future LLM Architecture

The LLM layer should be added only after API and persistence boundaries are
stable.

### Future Data Flow

```text
player text
  -> Intent Parser Agent
  -> structured action candidate
  -> validator
  -> rule_engine
  -> Narrator Agent
  -> validated response
```

### Agent Rule

```text
Agents may propose.
Validators and rule_engine decide.
Only validated state is persisted.
```

## Design Review Checklist

Before adding a new feature, ask:

1. Is this CLI-only, API-only, or reusable game logic?
2. Does it change game truth?
3. Should this live in route, schema, service, rule engine, or repository?
4. Does it need a test?
5. Does it require README, CHANGELOG, or design doc updates?

If a feature changes durable state or public API shape, update this document.
