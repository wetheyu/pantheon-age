# Future Phase Plan

This is the execution roadmap after the Phase 1-9 baseline.

It is written for small Codex-friendly development tasks: each stage should be
scoped, testable, and easy to review.

## Direction

```text
LLM provides imagination.
The program provides memory, consistency, validation, persistence, retrieval, and speed control.
Build foundations first. Polish after the foundations stop moving.
```

Completed and remaining order:

```text
Phase 7: Minimum Playable Experience Calibration
Phase 8: Progression And Core Mechanics
Phase 9: Web UI And API Product Experience
Phase 10: Engineering Quality And Final Experience Optimization
```

Why this order:

- Phase 6 already added world knowledge and long-term memory.
- Phase 7 made the current loop playable enough for repeated testing.
- Phase 8 added the first progression and core mechanics baseline.
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

Status: complete.

Goal: make world-mode comfortable enough to test for 20-30 minutes without
fighting the CLI, debug text, location drift, or unclear consequences.

Non-goals:

- full progression;
- final combat balance;
- web UI;
- production deployment;
- replacing the current Agentic Runtime architecture.

### Phase 7.1 Runtime Latency Baseline

Status: complete.

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

Implemented baseline:

- `AgenticTurnResult.runtime_trace` records branch, total elapsed time, and
  per-step timings;
- CLI debug mode prints compact trace information only when
  `PANTHEON_SHOW_RUNTIME=1`;
- `agentic_runtime.smoke_test` provides a manual branch/latency check for local
  and opt-in live LLM paths.

### Phase 7.2 Story Output Calibration

Status: complete.

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

Implemented baseline:

- local world-mode narrator now uses player-facing tabletop prose instead of
  system-report wording;
- local Scene/NPC/Event/Item fallback text avoids engineering words such as
  temporary slice, validator, commit, and world fact;
- high-risk violence messages use in-world pressure and unresolved consequence
  language instead of "system did not confirm" phrasing;
- Turn Director and Agentic Narrator prompts explicitly forbid debug-shaped
  player-facing terms.

### Phase 7.3 Opening And First Hook

Status: complete.

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

Implemented baseline:

- world-mode character setup now builds a structured `opening_profile` from
  origin country, city, class, faith, ethnicity, and background;
- `Character.to_public_dict()` exposes opening profile data for future API/UI
  rendering;
- CLI opening text now presents identity, faith legality context, city context,
  a first incident, a background-specific hook, and 2-4 natural action
  suggestions;
- openings differ by origin country/city and background without forcing fixed
  buttons or hard-coded quest rails.

### Phase 7.4 Location And Scene Continuity Pass

Status: complete.

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

Implemented baseline:

- `current_location` remains city-level truth; `current_scene_focus` handles
  concrete street/building/scene continuity;
- non-movement world actions preserve scene focus across repeated turns;
- explicit in-city movement updates only `current_scene_focus`;
- leaving a scene returns to the city default focus without changing city;
- cross-city travel requests create a travel-preparation scene and a
  `travel_request_recorded` effect, but do not teleport the player;
- local manual Agentic Runtime now generates Scene/NPC/Event/Item material after
  state commit, so local content follows the committed scene focus;
- prompts and validators now forbid direct city/location changes in world-mode
  baseline unless a future phase adds explicit travel authority.

### Phase 7.5 Dice And Consequence UX

Status: complete.

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

Implemented baseline:

- world-mode checks now record `risk_type`, readable risk label, roll margin,
  and an outcome tier: full success, partial success, costly failure, or hard
  failure;
- player-facing roll text shows d20, stat, action modifier, DC, outcome label,
  risk label, and margin only when a check happens;
- violence, social pressure, mobility risks, theft, escape, and occult pressure
  now commit different consequence shapes instead of sharing one generic result;
- lethal or permanent outcomes remain gated by explicit committed authority;
- tests cover full success, partial success, hard failure, visible dice math,
  and distinct social/theft/occult consequences.

### Phase 7.6 Playtest Checklist And Fixtures

Status: complete.

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

Implemented baseline:

- added `docs/playtest_checklist.md` as the 20-minute manual world-mode
  checklist covering opening, social pressure, investigation, prayer, travel,
  violence, and memory feel;
- added `agentic_runtime/playtest_fixtures.py` as a local-only executable
  fixture that runs the same experience path without real LLM calls;
- added fixture tests that assert safety properties instead of exact prose:
  no debug terms in player-facing text, no uncommitted death, no accidental
  city teleport, visible rolls for risky actions, and memory growth across play;
- Phase 7 has a repeatable local safety net for future playtest regressions.

### Phase 7.7 Creative GM Mode

Status: complete.

Goal: restore the intended project direction: LLM owns imagination; Python owns
authority, memory, dice, validation, and persistence.

Scope:

- `agentic_runtime/providers.py`
- `agentic_runtime/orchestrator.py`
- `prompts/creative_gm.md`
- `.env.example`
- live LLM smoke test

Tasks:

- add a GM-first live LLM path where player-facing narration is primary;
- keep only a minimal sidecar for risk checks, location intent, blockers, and
  denied effects;
- preserve Python validation, dice, memory, and state commit authority;
- make this the default live world-mode path for actual playtesting.

Done when:

- live play no longer feels like the LLM is filling rigid Scene/NPC/Event/Item
  forms first;
- runtime trace clearly shows `creative_gm`;
- local tests still prove the safety boundary;
- existing Turn Director path remains available as a fallback/compatibility path.

Implemented baseline:

- added `OpenAICreativeGMProvider`, which calls a dedicated Creative GM prompt
  and converts the result into the existing validated runtime contract;
- added `CreativeGMOutput`, where `narration_text` is the primary output and
  check/location/risk fields are only sidecar data for Python;
- `orchestrator` now reports the branch as `creative_gm`;
- `.env` live play defaults now enable `PANTHEON_CREATIVE_GM_MODE=1`;
- `.env.example` documents the Creative GM switch;
- Turn Director and older multi-agent paths remain available when Creative GM
  mode is disabled.
- Phase 7 is now ready to hand off into Phase 8 progression/core mechanics.

## Phase 8: Progression And Core Mechanics

Goal: turn character choices into meaningful mechanical differences.

Non-goals:

- final balance;
- MMO-style progression depth;
- huge skill tree;
- web UI.

### Phase 8.1 Character Model Migration

Status: complete.

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

Implemented baseline:

- added six future-facing attributes while preserving the old four-stat bridge;
- added class level, faith level, ascension rank, revelation, favor, devotion,
  progression skills, talents, prayers, burdens, and progression flags;
- exposed progression through public character state and CLI status;
- added old-save compatibility defaults.

### Phase 8.2 Minimal Class Skills

Status: complete.

Implemented baseline:

- added one Lv1 signature skill per class;
- made class skills provide small bonuses to matching world-mode checks;
- surfaced skill bonuses in roll output and `check_context`;
- exposed skill affordances in public progression state and LLM context packs;
- enforced natural 1 / natural 20 outcome handling so bonuses do not remove
  dice tension.

### Phase 8.3 Minimal Faith Talents And Prayers

Status: complete.

Implemented baseline:

- added one Lv1 talent and one prayer per major god;
- talents add small passive bonuses to matching checks;
- prayers consume `favor` and add active bonuses;
- hostile/restricted church legality can increase suspicion when prayer is
  invoked publicly;
- talent/prayer affordances are available to public state and LLM context packs.

### Phase 8.4 Generic Check System

Status: complete.

Implemented baseline:

- world-mode checks now use shared six-attribute profiles on top of the old
  four-stat compatibility bridge;
- roll results include `attribute_profile` and `attribute_modifier`;
- player-facing dice output explains the six-attribute contribution;
- class skills, faith talents, prayers, and attribute modifiers now share one
  modifier path.

### Phase 8.5 Ritual Advancement Slice

Status: complete.

Implemented baseline:

- explicit advancement attempts can target class level, faith level, or first
  ascension;
- advancement evaluation reports requirements, costs, rewards, and denial
  reasons;
- earned class advancement consumes `revelation` and grants one class-related
  attribute point;
- earned faith advancement consumes `revelation` and `favor`, then increases
  devotion;
- first ascension requires class level 2, faith level 2, enough resources, and
  adds a burden.

### Phase 8.6 Items And Relics Slice

Status: complete.

Implemented:

- `phase1_cli/items.py` defines rule-facing item categories and item effects
  while preserving the old inventory save format;
- public player state and context packs expose `item_affordances`;
- world-mode checks can apply explicit carried item bonuses;
- consumables can be removed from inventory when used in a check;
- direct consumable use can change HP, SAN, or Corruption through the commit
  layer;
- temporary generated item proposals still cannot directly grant inventory or
  clues.

Done:

- items can matter mechanically without letting LLM hand out free rewards.

### Phase 8.7 Phase 8 Final Integration

Status: complete.

Implemented:

- consolidate Phase 8 documentation;
- verify skill, talent, prayer, advancement, and item mechanics work together;
- update player-facing help/status text where needed;
- decide what belongs in Phase 9 versus later Phase 10 polish.

Done:

- Phase 8 is documented and verified as a single playable mechanical baseline.

## Phase 9: Web UI And API Product Experience

Goal: make the current game playable in a browser.

Non-goals:

- complex deployment;
- account system;
- production payment/auth;
- final art direction.

### Phase 9.1 API Shape For World Mode

Status: complete.

Tasks:

- ensure FastAPI endpoints can create world-mode games;
- expose clean action responses for frontend;
- hide runtime debug unless requested;
- document API examples.

Done when:

- frontend can create a character/game and submit actions without CLI-only
  behavior.

Implemented baseline:

- `GET /origins` returns playable origin countries, cities, ethnicities, and
  common background identities;
- `POST /games` accepts world-mode setup fields and returns `game_mode`,
  public state, opening text, and setup summary;
- `POST /games/{game_id}/actions` returns `story`, `state`, `mechanics`, and
  optional `debug` while preserving the legacy `response` payload;
- API tests cover origins, world-mode creation, action response shape, debug
  opt-in, and invalid origin configuration.

### Phase 9.2 Minimal Web App Scaffold

Status: complete.

Tasks:

- create a small `web_ui/` app;
- use React + TypeScript + Vite unless a later decision changes the stack;
- connect to FastAPI in dev.

Done when:

- browser can load a game shell and call health/classes/origins endpoints.

Implemented baseline:

- `web_ui/` contains a minimal React + TypeScript + Vite browser client;
- frontend reads `/health`, `/classes`, `/gods`, and `/origins`;
- API CORS allows local Vite origins by default;
- README documents API + web startup commands.

### Phase 9.3 Character Creation Flow

Status: complete.

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

Implemented baseline:

- browser character creation form collects name, origin, city, ethnicity, class,
  faith, and background identity;
- frontend calls `POST /games` with `game_mode=world`;
- successful creation displays `game_id`, location, identity summary, and
  opening narration;
- frontend still does not duplicate game rules, dice, validation, memory, or
  state commit logic.

### Phase 9.4 Chat-style Play Surface

Status: complete.

Tasks:

- add story log;
- add player input box;
- add loading/error states;
- show host narration cleanly.

Done when:

- user can play a few turns in browser.

Implemented baseline:

- created games now open a browser story log seeded with opening narration;
- player actions submit to `POST /games/{game_id}/actions`;
- host story responses, loading state, submit errors, and lightweight mechanics
  summaries render in the browser;
- debug/runtime payloads remain hidden by default.

### Phase 9.5 Character And World Panels

Status: complete.

Tasks:

- add character sheet panel;
- add status/inventory/clues/memory panels;
- show current country, city, and scene focus;
- keep panels display-only unless a command explicitly changes state.

Done when:

- browser view is easier to read than CLI without changing game rules.

Implemented baseline:

- browser play surface now shows read-only character identity, HP/SAN,
  suspicion, corruption, current city, scene focus, visited locations, six
  attributes, legacy stats, progression resources, skills, talents, prayers,
  burdens, inventory affordances, and clues;
- panels update from the public API state after each submitted action;
- frontend displays item affordances but does not execute item effects or mutate
  state.

### Phase 9.6 API/Web Playtest Pass

Status: complete.

Tasks:

- improve browser playtest flow;
- add opening action suggestions;
- handle game-over state and new character restart;
- add API smoke check;
- update README run instructions.

Done when:

- a new developer can run API + web UI locally from docs.

Implemented baseline:

- browser play surface now shows opening action suggestions from the public
  game state;
- players can start a new character from the active play surface;
- game-over state disables further action submission and displays ending text;
- story log auto-scrolls during play;
- `npm run smoke:api` checks the main browser-facing API path while FastAPI is
  running.

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

Start with Phase 10.1 Observability And Trace Records.

Reason: Phase 9 now has a browser-playable product slice. The next step is to
make weird turns explainable before adding broader evals, packaging, and final
demo polish.

Detailed Phase 9/10 execution guidance now lives in:

```text
docs/final_phase10_plan.md
```
