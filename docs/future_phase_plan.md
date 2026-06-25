# Future Phase Plan

This is the execution plan after Phase 6.

It is written for small Codex-friendly development tasks: each stage should be
scoped, testable, and easy to review.

## Direction

```text
LLM provides imagination.
The program provides memory, consistency, validation, persistence, retrieval, and speed control.
Build foundations first. Polish after the foundations stop moving.
```

Consolidated order:

```text
Phase 7: Minimum Playable Experience Calibration
Phase 8: Progression And Core Mechanics
Phase 9: Web UI And API Product Experience
Phase 10: Engineering Quality And Final Experience Optimization
```

Why this order:

- Phase 6 already added world knowledge and long-term memory.
- Phase 7 makes the current loop playable enough for repeated testing.
- Phase 8 adds actual game mechanics after the loop is comfortable.
- Phase 9 moves the playable loop into a browser.
- Phase 10 makes the whole project easier to debug, evaluate, deploy, and
  present.

## Task Format

When asking Codex to implement a stage, prefer this shape:

```text
Task:
[one small stage]

Scope:
[files or modules likely involved]

Constraints:
- keep unrelated files unchanged
- preserve tests
- keep network tests opt-in

Done when:
- [observable behavior]
- [tests or verification]
- [docs updated if behavior changes]
```

## Phase 7: Minimum Playable Experience Calibration

Goal: make world-mode comfortable enough to test for 20-30 minutes without
fighting the CLI, debug text, location drift, or unclear consequences.

Non-goals:

- full progression;
- final combat balance;
- web UI;
- production deployment;
- replacing the current Agentic Runtime architecture.

### Phase 7.1 Runtime Latency Baseline

Goal: understand and reduce obvious turn latency without changing game design.

Scope:

- `agentic_runtime/orchestrator.py`
- `agentic_runtime/providers.py`
- `phase1_cli/main.py`
- `docs/live_llm_testing.md`

Tasks:

- add compact per-turn timing to runtime/debug payloads;
- keep timing hidden unless `PANTHEON_SHOW_RUNTIME=1`;
- record which branch ran: local, Turn Director, fallback, or full multi-agent;
- add a small live-smoke command that can be run manually without affecting
  normal tests;
- document fast settings for playtesting.

Done when:

- normal CLI output stays clean;
- debug mode can show total turn time and provider branch;
- unit tests do not call network;
- user can compare fast and full paths deliberately.

### Phase 7.2 Story Output Calibration

Goal: make the CLI feel like a tabletop host, not a runtime report.

Scope:

- `prompts/turn_director.md`
- `prompts/agentic_narrator.md`
- `agentic_runtime/validators.py`
- `phase1_cli/story.py`

Tasks:

- remove remaining debug-shaped wording from player-facing narration;
- make generated text longer only when it adds useful scene, choice, or tension;
- prefer concrete NPC action, sensory detail, and next hooks;
- keep state/debug/status behind explicit commands;
- ensure narration does not claim uncommitted clues, kills, items, or travel.

Done when:

- five normal turns read like story responses;
- no “临时切片 / 本次不会自动授予” style engineering text appears in normal mode;
- validator tests still reject unauthorized death/reward/location claims.

### Phase 7.3 Opening And First Hook

Goal: make a new game start with enough identity, situation, and direction.

Scope:

- `phase1_cli/main.py`
- `phase1_cli/story.py`
- `phase1_cli/scenarios.py`
- `phase1_cli/character.py`
- `docs/world_bible.md` if opening canon changes

Tasks:

- polish country, city, class, faith, ethnicity, and identity selection flow;
- generate a short opening based on those choices;
- give 2-4 natural possible actions without forcing fixed buttons;
- make opening hooks differ by country/city/faith/background.

Done when:

- player knows who they are, where they are, and why this first scene matters;
- starting in different countries produces visibly different openings;
- tests cover public character origin fields.

### Phase 7.4 Location And Scene Continuity Pass

Goal: stop the game from moving the player unless the player actually moves.

Scope:

- `phase1_cli/game_state.py`
- `phase1_cli/scenarios.py`
- `agentic_runtime/context_pack.py`
- `agentic_runtime/state_commit.py`
- `agentic_runtime/world_slice.py`
- prompts that mention location continuity

Tasks:

- strengthen `current_location` as city-level truth;
- strengthen `current_scene_focus` as concrete local scene truth;
- make local actions preserve scene focus by default;
- allow explicit in-city movement to update scene focus;
- require explicit travel authorization to change city/country.

Done when:

- a 5-turn scene stays in the same place unless the player moves;
- “问水手/观察墙壁/检查桌子” does not teleport the player;
- “去前厅/离开码头/乘船去维拉尔” produces distinct local/travel handling.

### Phase 7.5 Dice And Consequence UX

Goal: make risk feel fair and visible.

Scope:

- `agentic_runtime/rule_arbiter_agent.py`
- `agentic_runtime/state_commit.py`
- `agentic_runtime/contracts.py`
- `phase1_cli/story.py`

Tasks:

- show dice math only when a check happens;
- show DC, attribute, roll, modifier, and result in readable form;
- distinguish attempt, partial success, full success, and failure;
- keep lethal outcomes gated by explicit authority;
- make violent/social/stealth/occult risks produce different consequence types.

Done when:

- “杀守卫” cannot simply become “守卫死了” without committed authority;
- high-risk actions show why they succeeded or failed;
- player can understand consequences without reading debug payloads.

### Phase 7.6 Playtest Checklist And Fixtures

Goal: make manual playtesting repeatable.

Scope:

- `docs/playtest_checklist.md`
- tests if small behavior can be asserted safely

Tasks:

- write a 20-minute CLI playtest checklist;
- include opening, social, investigation, violence, prayer, travel, and memory
  cases;
- define expected safety properties instead of exact LLM prose;
- record known acceptable rough edges.

Done when:

- every future phase can be checked against the same basic playtest path;
- regressions are easier to notice.

## Phase 8: Progression And Core Mechanics

Goal: turn character choices into meaningful mechanical differences.

Non-goals:

- final balance;
- MMO-style progression depth;
- huge skill tree;
- web UI.

### Phase 8.1 Character Model Migration

Scope:

- `phase1_cli/character.py`
- `phase1_cli/game_state.py`
- `phase2_api/schemas.py`
- save/load tests

Tasks:

- migrate toward the six-attribute model in `docs/progression_design.md`;
- preserve compatibility with old saves where possible;
- expose public state clearly for CLI/API/web.

Done when:

- character serialization round-trips;
- old minimal character data can still load or fail gracefully.

### Phase 8.2 Minimal Class Skills

Tasks:

- add one signature skill per class;
- make each skill usable by Agentic Runtime as an action affordance;
- validate that skills can help checks but not auto-win.

Done when:

- knight, mage, spy, ranger, priest, and alchemist feel different in play.

### Phase 8.3 Minimal Faith Talents And Prayers

Tasks:

- add one talent or prayer per major god;
- model favor, burden, or risk in a small way;
- keep hostile/illegal faith context relevant.

Done when:

- faith choice changes possible actions and risks.

### Phase 8.4 Generic Check System

Tasks:

- route common checks through shared check data;
- support combat, social, stealth, investigation, occult, travel, and ritual
  checks;
- keep the arbiter agent flexible but validator-controlled.

Done when:

- different actions can use consistent DC/result/consequence handling.

### Phase 8.5 Ritual Advancement Slice

Tasks:

- add class level and faith level;
- add ritual requirements for advancement;
- require cost, evidence, or story milestone before promotion.

Done when:

- the player can complete one small advancement path in test/demo form.

### Phase 8.6 Items And Relics Slice

Tasks:

- define item categories;
- allow temporary generated items to become real only after validated commit;
- add simple equipment effects without bloating combat.

Done when:

- items can matter mechanically without letting LLM hand out free rewards.

## Phase 9: Web UI And API Product Experience

Goal: make the current game playable in a browser.

Non-goals:

- complex deployment;
- account system;
- production payment/auth;
- final art direction.

### Phase 9.1 API Shape For World Mode

Tasks:

- ensure FastAPI endpoints can create world-mode games;
- expose clean action responses for frontend;
- hide runtime debug unless requested;
- document API examples.

Done when:

- frontend can create a character/game and submit actions without CLI-only
  behavior.

### Phase 9.2 Minimal Web App Scaffold

Tasks:

- create a small `web_ui/` app;
- use React + TypeScript + Vite unless a later decision changes the stack;
- connect to FastAPI in dev.

Done when:

- browser can load a game shell and call health/classes/origins endpoints.

### Phase 9.3 Chat-style Play Surface

Tasks:

- add story log;
- add player input box;
- add loading/error states;
- show host narration cleanly.

Done when:

- user can play a few turns in browser.

### Phase 9.4 Character And World Panels

Tasks:

- add character sheet panel;
- add status/inventory/clues/memory panels;
- show current country, city, and scene focus;
- keep panels display-only unless a command explicitly changes state.

Done when:

- browser view is easier to read than CLI without changing game rules.

### Phase 9.5 API Product Polish

Tasks:

- improve API errors;
- add timeout/fallback messages;
- align response shapes with frontend needs;
- update README run instructions.

Done when:

- a new developer can run API + web UI locally from docs.

## Phase 10: Engineering Quality And Final Experience Optimization

Goal: make the project reliable, explainable, cheaper to operate, and demo-ready.

### Phase 10.1 Observability And Trace Records

Tasks:

- log prompt name, model, provider branch, latency, token estimate, validation
  result, fallback reason, and commit result;
- keep secrets out of logs;
- make traces opt-in or local-safe.

Done when:

- bad turns can be debugged without guessing which agent failed.

### Phase 10.2 Evals And Safety Fixtures

Tasks:

- add prompt-injection cases;
- test no free items, no unauthorized death, no secret leaks, no invented core
  gods, no uncommitted travel;
- test memory visibility boundaries.

Done when:

- important agent regressions are caught before manual playtesting.

### Phase 10.3 Quality Evals

Tasks:

- build sample scenes;
- score coherence, player agency, next hooks, canon grounding, and pacing;
- compare model/settings combinations.

Done when:

- prompt/model changes can be compared with evidence.

### Phase 10.4 Cost And Speed Optimization

Tasks:

- shrink schemas and prompts based on traces;
- cache stable canon retrieval;
- compare keyword/vector/hybrid retrieval;
- choose fast/default and high-quality/manual modes.

Done when:

- normal play has an acceptable latency/cost profile.

### Phase 10.5 Local Model Provider

Tasks:

- support OpenAI-compatible local endpoints;
- document local model limitations;
- keep validators identical across providers.

Done when:

- the game can run against a local-compatible provider for experiments.

### Phase 10.6 Docker And Dev Profiles

Tasks:

- add Docker or Docker Compose for API/web/database where useful;
- keep `.env` examples safe;
- document local/dev/demo profiles.

Done when:

- another machine can run the project without hand-reconstructing setup.

### Phase 10.7 Final Demo Pass

Tasks:

- choose one polished demo path;
- tune opening, pacing, progression slice, UI, prompts, and model settings
  together;
- write resume/interview explanation notes.

Done when:

- the project has one reliable demo path that shows Agentic Runtime, RAG,
  memory, validation, progression, and UI working together.

## Recommended Next Task

Start with Phase 7.1 Runtime Latency Baseline.

Reason: speed and debug visibility affect every later playtest, but this task
does not force major gameplay design decisions.
