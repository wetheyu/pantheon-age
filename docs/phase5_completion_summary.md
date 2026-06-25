# Phase 5 Completion Summary

Phase 5 completes the project's first Agentic Runtime baseline.

It replaces the old idea of "LLM fills a narrow action schema" with a staged
agent loop:

```text
Player input
  -> Memory Retriever
  -> Turn Director Agent
  -> Validator Layer
  -> State Commit Layer
  -> Memory Curator Agent
  -> Memory Store
  -> Narration Branch Selection
  -> CLI output
```

## Core Principle

```text
LLM provides imagination.
Agents organize possibilities.
Programs validate, commit, remember, and audit.
```

The rule system does not exist to limit imagination. It exists to prevent LLM
weaknesses from becoming game truth: context drift, inconsistent standards,
uncontrolled rewards, forgotten facts, hidden-information leaks, and unverified
world changes.

## Completed Capabilities

- Open player intent is preserved through `OpenActionProposal`.
- Rule adjudication is separated from state commit.
- Tutorial mode remains compatible with the deterministic Mist Abbey scenario.
- World mode starts from one of eight important countries.
- Origin country, starting city, ethnicity, common background identity, and local
  church legality flow into Agentic Runtime memory.
- Temporary Scene / NPC / Event / Item Agents can generate world content.
- Optional OpenAI-backed Turn Director provider is available behind provider
  boundaries; it proposes open intent, contextual rule adjudication,
  Scene/NPC/Event/Item content, and compact narration
  in one categorized call for normal live play.
- Optional legacy OpenAI-backed Intent / Rule Arbiter / WorldBundle providers
  remain available by disabling `PANTHEON_AGENTIC_TURN_DIRECTOR`.
- Optional full OpenAI NPC / Event / Item / Narrator providers are available for
  slower, more model-heavy agent-level experiments.
- Local providers remain available as deterministic fallback.
- Memory candidates are validated before persistence.
- Local memory store separates `player_known`, `npc_known`, `location`, `quest`,
  and `secret` memory buckets.
- Visible memory enters later turns through Memory Retriever.
- Secret memory stays out of public state, default runtime serialization, and
  player-facing narration.
- World-mode CLI output now renders player-facing story text with temporary
  scene, NPC, event, and item content.
- World-mode actions are committed as `world_action` records and do not
  automatically grant clues, inventory, location changes, faction changes, or
  progression rewards.
- Tests cover the core Phase 5 path without live network calls.

## Current Boundaries

- `agentic_runtime/` owns Phase 5 orchestration.
- `llm_runtime/` remains the older Phase 4 structured LLM proposal runtime.
- `phase1_cli/main.py` remains CLI-only.
- `phase1_cli/game_service.py` exposes reusable service behavior.
- `phase1_cli/rule_engine.py` remains the deterministic rule boundary.
- `State Commit Layer` is still the only Phase 5 layer that writes game reality.
- LLM-backed agents can propose content, but cannot directly mutate `GameState`.

## Not Yet Included

Phase 5 intentionally does not include:

- full web UI;
- full vector RAG;
- full combat rewrite;
- full progression implementation;
- database-backed long-term memory;
- all agents running through live LLM calls;
- automatic permanent open-world facts without validators.

These are future phases, not Phase 5 scope.

## How To Try The Phase 5 Slice

Use world mode:

```text
PANTHEON_GAME_MODE=world
```

Then run:

```bash
./.venv/bin/python -m phase1_cli.main
```

To use the implemented low-latency OpenAI-backed Phase 5 Turn Director:

```text
PANTHEON_USE_AGENTIC_LLM=1
PANTHEON_AGENTIC_TURN_DIRECTOR=1
OPENAI_API_KEY=...
```

To debug the older multi-call Intent / Rule Arbiter / WorldBundle path:

```text
PANTHEON_AGENTIC_TURN_DIRECTOR=0
```

To route NPC / Event / Item / Narrator agents through separate OpenAI calls:

```text
PANTHEON_AGENTIC_FULL_LLM=1
```

Ordinary tests do not call live LLM APIs.

Set `PANTHEON_SHOW_RUNTIME=1` only when you want to inspect Agentic Runtime
debug details.
