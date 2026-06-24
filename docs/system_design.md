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
