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

Verification:

```bash
./.venv/bin/python -m unittest tests.test_agentic_runtime tests.test_phase2_api
```

## Phase 10.2 Agent Safety Evals

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
env PANTHEON_USE_AGENTIC_LLM=0 PANTHEON_USE_LLM=0 ./.venv/bin/python -m unittest discover -s tests
```

## Phase 10.3 Narrative Quality Evals

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
./.venv/bin/python -m unittest tests.test_story_views tests.test_playtest_fixtures
```

## Phase 10.4 Cost And Speed Optimization

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
