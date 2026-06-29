# Final Phase 10 Plan

Phase 10 is the final engineering and demo-quality phase after the Phase 1-9
baseline.

It should not create a second game system. It should make the existing
Agentic Runtime, RAG, memory, progression, API, and Web UI easier to debug,
evaluate, optimize, run, and present.

## Core Rule

```text
Do not expand scope before the current loop is measurable.
Do not optimize blindly before traces exist.
Do not replace Agentic Runtime with frontend logic.
Do not let live LLM output bypass validators or state commit.
```

## Phase 10.1 Observability And Trace Records

Status: complete.

Goal:

- make every weird turn explainable.

Tasks:

- add a structured trace object for API/CLI world-mode turns;
- include provider branch, prompt name, model, latency, fallback reason,
  validation result, committed effects, and memory writes;
- keep secrets and hidden memory out of logs;
- expose traces only when debug is explicitly enabled;
- make browser/API debug output opt-in.

Likely files:

- `agentic_runtime/contracts.py`
- `agentic_runtime/orchestrator.py`
- `agentic_runtime/providers.py`
- `phase1_cli/game_service.py`
- `phase2_api/services/session_store.py`
- `phase2_api/schemas.py`
- `tests/test_agentic_runtime.py`
- `tests/test_phase2_api.py`

Done when:

- local tests can assert trace shape without network;
- API action response can include trace only when requested;
- normal player-facing story remains clean.

Implemented:

- added `agentic_runtime/observability.py` for safe structured runtime summaries;
- API default responses hide `response.llm_runtime`;
- API debug responses include `debug.observability` and full runtime only when
  `include_debug=true`;
- CLI runtime debug output includes observability summary;
- tests cover observability shape, API hiding behavior, and local/offline test
  isolation.

Verification:

```bash
./.venv/bin/python -m unittest tests.test_agentic_runtime tests.test_phase2_api
```

## Phase 10.2 Agent Safety Evals

Status: complete.

Goal:

- catch authority and safety regressions before manual playtesting.

Eval cases:

- prompt injection;
- free item attempts;
- unauthorized death;
- invented ninth core god;
- secret leakage;
- uncommitted city travel;
- scene teleportation;
- impossible wealth/property action;
- memory visibility mistakes;
- religion legality pressure misuse.

Tasks:

- create an `evals/` package or `agentic_runtime/evals.py` if simpler;
- define fixture inputs and expected safety properties;
- keep default evals local/offline;
- add optional live LLM eval mode only behind explicit environment variables.

Likely files:

- `agentic_runtime/playtest_fixtures.py`
- `tests/test_playtest_fixtures.py`
- `tests/test_agentic_runtime.py`
- `docs/playtest_checklist.md`
- `docs/live_llm_testing.md`

Done when:

- local evals fail if the runtime grants free rewards, kills NPCs without
  authority, leaks secrets, or teleports the player;
- live evals are available but never run accidentally.

Verification:

```bash
./.venv/bin/python -m unittest tests.test_safety_evals
```

Implemented:

- added `agentic_runtime/safety_evals.py` for repeatable local/offline safety
  evals;
- added `tests/test_safety_evals.py`;
- evals cover free reward attempts, unauthorized death, secret leakage, invented
  ninth core god, uncommitted cross-city travel, impossible major purchase, and
  scene continuity after setup;
- fixed cross-city travel detection so explicit attempts to reach another city
  become travel requests rather than direct location changes;
- fixed blocked acquisition narration validation so quoted player intent is not
  mistaken for confirmed property ownership.

Additional verification:

```bash
./.venv/bin/python -m unittest tests.test_playtest_fixtures tests.test_agentic_runtime
```

## Phase 10.3 Narrative Quality Evals

Status: complete.

Goal:

- make prompt/model changes comparable with evidence.

Quality dimensions:

- player agency;
- concrete sensory detail;
- canon grounding;
- scene continuity;
- next actionable hook;
- no backend/debug vocabulary;
- no uncommitted rewards;
- pacing and readability.

Tasks:

- create repeatable sample turns;
- score narration with deterministic heuristics first;
- optionally add live/model-assisted scoring later;
- record before/after examples in docs without exposing secrets.

Likely files:

- `agentic_runtime/playtest_fixtures.py`
- `tests/test_story_views.py`
- `prompts/creative_gm.md`
- `prompts/turn_director.md`
- `docs/playtest_checklist.md`

Done when:

- a prompt change can be evaluated against the same sample turns;
- poor outputs like “系统裁定报告” or raw proposal labels are caught.

Verification:

```bash
./.venv/bin/python -m unittest tests.test_narrative_quality_evals tests.test_story_views tests.test_playtest_fixtures
```

Implemented:

- added `agentic_runtime/narrative_quality_evals.py` for deterministic local
  story-quality scoring;
- added `tests/test_narrative_quality_evals.py`;
- evals check second-person player agency, concrete/sensory detail, location
  grounding, next actionable hook, paragraph pacing, backend/runtime term leaks,
  and report-style labels;
- fixed memory curation so committed effect ids are converted into
  player-facing summaries before becoming visible long-term memory;
- added defensive visible-memory filtering for old records that may contain
  backend effect ids.

## Phase 10.4 Cost And Speed Optimization

Status: complete.

Goal:

- make normal play responsive and cost-aware without weakening imagination.

Tasks:

- measure end-to-end API turn latency;
- split latency into retrieval, provider, validation, commit, persistence, and
  response serialization;
- define play profiles: `local`, `fast`, `quality`, `debug`;
- reduce context pack size based on traces;
- cache stable canon retrieval where useful;
- compare keyword, local hybrid, vector, and vector_hybrid retrieval;
- document recommended defaults for playtesting and demos.

Likely files:

- `agentic_runtime/context_pack.py`
- `agentic_runtime/orchestrator.py`
- `rag/canon.py`
- `rag/vector_store.py`
- `phase2_api/services/session_store.py`
- `.env.example`
- `README.md`

Done when:

- default play has a documented latency/cost profile;
- high-quality mode remains available for experiments;
- debug mode explains why a turn was slow.

Verification:

```bash
./.venv/bin/python -m agentic_runtime.smoke_test
npm run smoke:api
```

Implemented:

- added `agentic_runtime/runtime_profiles.py`;
- added `agentic_runtime/performance.py`;
- added `tests/test_runtime_profiles.py` and `tests/test_performance.py`;
- `PANTHEON_PLAY_PROFILE` now supports `local`, `fast`, `quality`, and `debug`;
- `fast` profile uses the one-call Creative GM path with compact context and
  shorter narration guidance;
- `quality` profile keeps more context/output budget for important scenes;
- `debug` profile enables runtime output while keeping the same validation and
  commit boundaries;
- `agentic_runtime.smoke_test` now reports runtime profile, slowest steps,
  budget status, and speed advice;
- real LLM smoke testing confirmed the provider call dominates latency while
  local memory, validation, commit, and persistence remain tiny.

Observed live smoke:

```text
PANTHEON_PLAY_PROFILE=fast
branch=creative_gm
total ~= 17-23s in current runs
dominant step=creative_gm_provider
status=warn against a 20s fast-profile budget
```

## Phase 10.5 Provider Strategy And Local Model Path

Goal:

- support OpenAI and local OpenAI-compatible providers without changing game
  authority rules.

Tasks:

- document provider environment variables clearly;
- support configurable base URL if not already covered;
- add smoke tests for provider configuration without requiring network;
- document local model limitations for JSON reliability and narration quality;
- keep validators identical across OpenAI/local/fallback providers.

Candidate local runtimes:

- Ollama;
- LM Studio;
- vLLM;
- any OpenAI-compatible local endpoint.

Likely files:

- `llm_runtime/providers.py`
- `agentic_runtime/providers.py`
- `.env.example`
- `docs/live_llm_testing.md`
- `docs/technical_roadmap.md`

Done when:

- OpenAI, local-compatible, and fallback modes share the same runtime boundary;
- switching provider does not require code edits.

Verification:

```bash
./.venv/bin/python -m unittest tests.test_llm_runtime_providers
```

Status: complete in `v10.5.0`.

Implemented:

- added `PANTHEON_OPENAI_PROVIDER` and `PANTHEON_OPENAI_BASE_URL`;
- `build_openai_client()` now supports official OpenAI and custom
  OpenAI-compatible base URLs;
- custom OpenAI-compatible endpoints use a chat-completions JSON path, so local
  servers do not need to implement the newer Responses API;
- runtime provider summaries include a safe endpoint summary without exposing
  API keys or raw payloads;
- `agentic_runtime.smoke_test` prints provider endpoint information;
- added offline tests for custom base URL client construction and Agentic
  Runtime endpoint reporting;
- documented Ollama, LM Studio, vLLM, and generic local compatible setup.

Verification run:

```bash
./.venv/bin/python -m unittest tests.test_llm_runtime_providers tests.test_runtime_profiles
```

## Phase 10.6 Packaging And Dev Profiles

Goal:

- make setup repeatable on another machine.

Tasks:

- decide whether Docker Compose is worth adding for API + Web + SQLite;
- define local/dev/demo/test profiles;
- keep `.env.example` safe and complete;
- make ignored runtime folders clear;
- document one-command-ish startup paths where practical.

Likely files:

- `README.md`
- `.env.example`
- `.gitignore`
- `web_ui/README.md`
- optional `Dockerfile` / `docker-compose.yml`

Done when:

- a new developer can run CLI, API, Web, tests, and API smoke from docs;
- runtime databases, saves, build output, keys, and caches stay untracked.

Verification:

```bash
git status --ignored --short
npm run build
```

Status: complete in `v10.6.0`.

Implemented:

- added `scripts/dev.py` as a standard-library developer helper;
- `scripts/dev.py doctor` reports local setup status without reading secrets;
- `scripts/dev.py check` runs Python compile plus the offline unit test suite
  with live LLM and live embeddings disabled;
- added helper commands for CLI, API, Agentic Runtime smoke, Web install, Web
  dev, Web build, and Web API smoke;
- added `docs/dev_setup.md` for repeatable setup, profile usage, official
  OpenAI/local endpoint config, common commands, local runtime files, and the
  Docker decision;
- expanded `.gitignore` for local env variants, SQLite sidecar files, logs,
  caches, coverage, build output, and web runtime output;
- updated README, Web README, docs index, changelog, AGENTS, and technical
  roadmap to the packaging/dev-profile baseline.

Docker decision:

- defer Docker Compose until the final demo path is locked;
- current recommended development path is `.venv` + FastAPI + Vite +
  `scripts/dev.py`;
- SQLite and local model providers do not currently require container
  orchestration.

## Phase 10.7 Final Demo Pass

Goal:

- produce one polished demo path for portfolio/interview use.

Demo route should show:

- world-mode character creation;
- opening hook;
- canon/RAG grounding;
- memory continuity over several turns;
- risky action with visible dice;
- prayer or item use;
- progression visibility;
- validation preventing an impossible reward or unauthorized death;
- browser UI.

Tasks:

- choose one recommended origin/class/faith/background setup;
- write a 5-10 minute demo script;
- tune prompt/context/profile defaults for that route;
- update README with “what this project demonstrates”;
- add final smoke checklist.

Likely files:

- `README.md`
- `docs/playtest_checklist.md`
- `docs/final_demo.md`
- `web_ui/README.md`
- `prompts/creative_gm.md`

Done when:

- the project has one repeatable, impressive demo path;
- the README can explain the project as an AI Agent engineering portfolio piece.

Verification:

```bash
npm run build
npm run smoke:api
env PANTHEON_RUN_LIVE_LLM_TESTS=1 PANTHEON_USE_AGENTIC_LLM=1 ./.venv/bin/python -m unittest tests.test_live_agentic_runtime
```

Status: complete in `v10.7.0`.

Implemented:

- added `docs/final_demo.md` as the recommended 5-10 minute portfolio route;
- added `agentic_runtime/final_demo.py` with a local final demo smoke route;
- added `tests/test_final_demo.py` to keep the route from regressing;
- added `scripts/dev.py final-demo`;
- updated Web UI copy from internal phase wording to final demo wording;
- added a browser character-creation shortcut for the recommended final demo
  setup: 卢米埃 / 卢塞恩 / 密探 / 隐秘之神 / 调查记者;
- updated Web API smoke to use the final demo setup;
- updated README with what the project demonstrates as an AI Agent engineering
  portfolio piece.

Final demo route demonstrates:

- world-mode character creation and opening hook;
- canon/context grounding;
- memory continuity;
- item bonus in dice context;
- prayer bonus and religious legality pressure;
- resource gate preventing impossible property acquisition;
- violence gate preventing unauthorized death confirmation;
- browser UI.

## Recommended Execution Order

```text
Phase 10.1 Observability And Trace Records
Phase 10.2 Agent Safety Evals
Phase 10.3 Narrative Quality Evals
Phase 10.4 Cost And Speed Optimization
Phase 10.5 Provider Strategy And Local Model Path
Phase 10.6 Packaging And Dev Profiles
Phase 10.7 Final Demo Pass
```

Reason:

- observability must come before optimization;
- safety evals must come before broad prompt changes;
- quality evals make prompt/model choices measurable;
- speed/cost work should use traces and evals;
- provider strategy belongs after the current OpenAI path is measurable;
- packaging should happen after defaults settle;
- final demo should happen last.
