# Phase 9-10 Execution Plan

This plan starts after the Phase 1-8 baseline.

Phase 9 productizes the current game loop in a browser. Phase 10 makes the
project easier to evaluate, debug, optimize, deploy, and present.

## Design Rule

```text
Phase 9 builds a better surface for the existing runtime.
Phase 10 improves reliability and demo quality.
Neither phase should create a second rules engine.
```

The web UI and API must use the existing service/runtime/commit layers:

```text
Browser
  -> FastAPI route
  -> phase1_cli.game_service
  -> Agentic Runtime
  -> validators
  -> state commit
  -> persistence
  -> API response
  -> browser story/state UI
```

## Phase 9: Web UI And API Product Experience

Goal: make the current game playable in a browser.

Non-goals:

- account system;
- multiplayer;
- payment/auth;
- production deployment;
- new progression rules;
- replacing Agentic Runtime.

### Phase 9.1 API Contract Cleanup

Goal: ensure the browser can create and play a world-mode game cleanly.

Tasks:

- review current FastAPI response shapes;
- add or refine endpoints for world-mode setup data;
- make action responses separate player-facing text from debug/runtime payloads;
- make runtime debug opt-in through query/body flag or environment setting;
- document example requests for creating a world game and submitting actions.

Likely files:

- `phase2_api/schemas.py`
- `phase2_api/routes/games.py`
- `phase2_api/routes/classes.py`
- `phase2_api/routes/gods.py`
- `phase2_api/routes/locations.py`
- `phase2_api/services/session_store.py`
- `docs/phase2_api_plan.md`

Done when:

- API can create a world-mode game with origin/class/god/background choices;
- API can submit an action and return story text, roll summary, public state,
  committed effects, and optional debug;
- tests cover the API contract.

### Phase 9.2 Web App Scaffold

Goal: add a minimal browser client without over-designing.

Default stack:

- React;
- TypeScript;
- Vite;
- plain CSS first unless a design system is clearly needed.

Tasks:

- create `web_ui/`;
- add dev scripts and README instructions;
- connect to FastAPI health/classes/gods/origins endpoints;
- keep environment config simple.

Done when:

- `web_ui` can run locally;
- browser shows a minimal shell and confirms API connection;
- no game rules are duplicated in frontend code.

### Phase 9.3 Character Creation Flow

Goal: replace CLI prompts with a simple browser setup screen.

Tasks:

- choose origin country;
- choose starting city where applicable;
- choose class;
- choose faith;
- choose background identity;
- create game session through API;
- show opening narration.

Done when:

- a player can start world-mode from browser without using terminal prompts.

### Phase 9.4 Chat-Style Play Surface

Goal: make the browser feel like a tabletop host conversation.

Tasks:

- display story log;
- add player input box;
- show loading state while host thinks;
- show errors and fallback messages cleanly;
- keep debug collapsed or hidden by default;
- prevent double-submit while an action is pending.

Done when:

- player can play multiple turns in browser;
- story text is more readable than CLI output;
- runtime/debug data does not pollute normal play.

### Phase 9.5 Character And World Panels

Goal: make state readable without interrupting the story.

Panels:

- character identity;
- HP/SAN/Suspicion/Corruption;
- six attributes;
- class skill, faith talent, prayers;
- inventory and item affordances;
- advancement options and missing requirements;
- current country/city/scene focus;
- clues and visible memory.

Done when:

- browser makes Phase 8 mechanics understandable at a glance;
- panels are display-only unless a real action command changes state.

### Phase 9.6 API/Web Playtest Pass

Goal: prove the browser path works as a product slice.

Tasks:

- run a 10-20 minute browser playtest;
- check opening, social action, risky action, prayer, item use, and advancement;
- fix API shape friction discovered by UI;
- update README with API + web commands.

Done when:

- a new user can run API + web locally and play a short session.

## Phase 10: Engineering Quality And Final Experience Optimization

Goal: make the project reliable, debuggable, cost-aware, and demo-ready.

Non-goals:

- endless feature expansion;
- rewriting the UI;
- replacing the runtime architecture.

### Phase 10.1 Observability

Goal: make bad turns explainable.

Tasks:

- record provider branch, prompt name, model, latency, validation result,
  fallback reason, committed effects, and token/cost estimate where available;
- keep API keys and hidden memory out of logs;
- expose traces only in debug mode.

Done when:

- a failed or weird turn can be inspected without guessing which layer failed.

### Phase 10.2 Agent Evals And Regression Fixtures

Goal: catch important LLM/runtime failures before manual playtesting.

Eval cases:

- prompt injection;
- free item attempts;
- unauthorized death;
- secret leakage;
- invented ninth core god;
- uncommitted travel;
- memory visibility mistakes;
- impossible wealth/property actions;
- scene teleportation.

Done when:

- eval fixtures can be run locally without network by default;
- optional live LLM evals are gated by environment variables.

### Phase 10.3 Narrative Quality Evals

Goal: compare prompt/model changes with evidence.

Scoring dimensions:

- agency;
- coherence;
- canon grounding;
- concrete sensory detail;
- next hooks;
- pacing;
- no debug-text leakage;
- no uncommitted rewards.

Done when:

- prompt/model changes can be compared on repeatable sample turns.

### Phase 10.4 Cost And Speed Optimization

Goal: make normal play fast enough and affordable enough.

Tasks:

- profile API and browser turn latency;
- compare Creative GM, Turn Director, and full multi-agent modes;
- tune context pack size;
- cache stable canon retrieval;
- compare keyword/vector/hybrid retrieval;
- define `fast`, `quality`, and `debug` profiles.

Done when:

- default play uses a sensible latency/cost profile;
- high-quality mode remains available for manual experiments.

### Phase 10.5 Provider Strategy

Goal: support experimentation without changing game logic.

Tasks:

- support OpenAI-compatible local endpoints;
- document provider environment variables;
- keep validators identical across providers;
- record limitations of local models.

Done when:

- OpenAI, local-compatible, and fallback paths share the same authority rules.

### Phase 10.6 Packaging And Dev Profiles

Goal: make setup repeatable.

Tasks:

- decide whether Docker/Docker Compose is useful for API + web + SQLite;
- document dev/test/demo profiles;
- keep `.env.example` safe;
- avoid committing runtime databases or saves.

Done when:

- another machine can run the project without reconstructing setup from chat.

### Phase 10.7 Final Demo Pass

Goal: create one reliable demo path for portfolio/interview use.

Demo should show:

- world-mode opening;
- RAG/canon grounding;
- memory continuity;
- risky action with visible dice;
- prayer or item use;
- advancement or progression visibility;
- validation preventing an impossible reward or death;
- browser UI.

Done when:

- there is one polished, repeatable demo route;
- README explains what to run and what the project demonstrates.

## Recommended Implementation Order

```text
Phase 9.1 API Contract Cleanup
Phase 9.2 Web App Scaffold
Phase 9.3 Character Creation Flow
Phase 9.4 Chat-Style Play Surface
Phase 9.5 Character And World Panels
Phase 9.6 API/Web Playtest Pass
Phase 10.1 Observability
Phase 10.2 Agent Evals And Regression Fixtures
Phase 10.3 Narrative Quality Evals
Phase 10.4 Cost And Speed Optimization
Phase 10.5 Provider Strategy
Phase 10.6 Packaging And Dev Profiles
Phase 10.7 Final Demo Pass
```
