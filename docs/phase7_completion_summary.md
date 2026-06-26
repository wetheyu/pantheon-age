# Phase 7 Completion Summary

Phase 7 closes the first minimum playable experience calibration pass for
Pantheon Age world-mode.

The goal of this phase was not to finish all game mechanics. The goal was to
make the existing Agentic Runtime loop comfortable enough to play, test, and
iterate without fighting debug text, unclear openings, accidental teleportation,
binary risk handling, or unrepeatable playtests.

## Status

```text
Phase 7: complete
Next phase: Phase 8 Progression And Core Mechanics
```

## Completed Stages

### Phase 7.1 Runtime Latency Baseline

Runtime results now include a compact trace with:

- active runtime branch;
- total elapsed time;
- per-step timings.

The CLI only shows trace data when `PANTHEON_SHOW_RUNTIME=1`, so normal play
stays clean.

### Phase 7.2 Story Output Calibration

World-mode narration was moved away from system reports and toward tabletop GM
responses.

Player-facing narration should not expose terms such as validator, commit,
rule_result, temporary slice, or world fact.

### Phase 7.3 Opening And First Hook

World-mode character setup now creates an `opening_profile` from:

- origin country;
- starting city;
- class;
- faith;
- ethnicity when relevant;
- background identity.

The opening introduces who the player is, where they are, what pressure is
already present, and a few natural actions they can try.

### Phase 7.4 Location And Scene Continuity

World-mode now separates:

- `current_location`: city-level truth;
- `current_scene_focus`: concrete local scene.

Non-movement actions preserve scene focus. In-city movement changes only scene
focus. Cross-city travel is recorded as preparation/request, not instant
teleportation.

### Phase 7.5 Dice And Consequence UX

High-risk actions now show readable dice results when a check occurs:

- d20 roll;
- attribute;
- action modifier;
- DC;
- risk type;
- margin;
- outcome tier.

Outcome tiers are:

- full success;
- partial success;
- costly failure;
- hard failure.

Violence, social pressure, stealth, theft, escape, and occult pressure now have
different consequence shapes. Success can create leverage or an opening, but it
does not automatically grant death, permanent injury, clues, items, faction
changes, or rewards.

### Phase 7.6 Playtest Checklist And Fixtures

Phase 7 now has a repeatable manual checklist and an automated local fixture:

- `docs/playtest_checklist.md`;
- `agentic_runtime/playtest_fixtures.py`;
- `tests/test_playtest_fixtures.py`.

The fixture checks safety properties instead of exact prose, so it remains
useful even when LLM wording changes.

### Phase 7.7 Creative GM Mode

The live LLM path was corrected to follow the project's core principle:

```text
LLM owns imagination.
Python owns authority.
```

Creative GM mode makes `narration_text` the primary model output. The structured
fields become a sidecar for Python to validate risk, dice, location intent,
blockers, and forbidden effects.

This replaces the feeling of the model filling rigid Scene/NPC/Event/Item forms
before it is allowed to act as a GM.

## Current Playable Baseline

The current world-mode loop can:

- create a character with origin, city, faith, class, and background context;
- introduce a playable opening situation;
- accept open-ended natural-language actions;
- retrieve compact lore and memory context;
- produce player-facing story output;
- run a high-freedom Creative GM live LLM branch for actual playtesting;
- preserve local scene continuity;
- adjudicate high-risk actions with visible dice;
- write validated memory records;
- run local/offline tests without API cost;
- optionally use real LLM providers for live smoke testing.

## Important Boundaries

The program should constrain authority, not imagination.

Allowed LLM role:

- propose scenes, NPCs, events, items, narration, risks, blockers, and hooks;
- preserve player intent;
- make the world feel alive.

Program authority:

- validate proposals;
- roll dice;
- commit state;
- preserve memory;
- prevent hidden facts, rewards, death, travel, or faction changes from becoming
  truth without permission.

## Verification

Phase 7 completion should be verified with:

```bash
./.venv/bin/python -m py_compile phase1_cli/*.py phase2_api/*.py phase2_api/routes/*.py phase2_api/services/*.py phase3_persistence/*.py agentic_runtime/*.py llm_runtime/*.py rag/*.py tests/*.py
env PANTHEON_USE_AGENTIC_LLM=0 PANTHEON_USE_LLM=0 PANTHEON_EMBEDDING_PROVIDER=local PANTHEON_CANON_RETRIEVAL=keyword ./.venv/bin/python -m unittest discover -s tests
env PANTHEON_USE_AGENTIC_LLM=0 PANTHEON_USE_LLM=0 PANTHEON_EMBEDDING_PROVIDER=local PANTHEON_CANON_RETRIEVAL=keyword ./.venv/bin/python -m agentic_runtime.smoke_test
```

Optional real LLM smoke test:

```bash
PANTHEON_USE_AGENTIC_LLM=1 PANTHEON_AGENTIC_TURN_DIRECTOR=1 ./.venv/bin/python -m agentic_runtime.smoke_test
```

Latest completion check:

- local unit suite: passed;
- local Agentic Runtime smoke: passed;
- live Agentic Runtime smoke: passed on the `turn_director` branch;
- live smoke used local keyword canon retrieval and local embedding settings to
  keep the test focused on the LLM turn director path.

After the Creative GM correction, live play should prefer:

```text
PANTHEON_CREATIVE_GM_MODE=1
```

and runtime trace should report:

```text
Branch: creative_gm
```

## Remaining Rough Edges

These are intentionally left for later phases:

- progression is still shallow;
- class skills and faith prayers do not yet meaningfully change the loop;
- travel is still preparation/request, not a full journey system;
- rewards, clue economy, inventory growth, and ritual advancement need Phase 8;
- Web UI starts in Phase 9;
- broader evals, deployment, and final polish belong to Phase 10.

## Phase 8 Handoff

Phase 8 should start by making character choices matter mechanically.

Recommended first stage:

```text
Phase 8.1 Character Model Migration
```

This should migrate toward the six-attribute model in
`docs/progression_design.md` while preserving save/API compatibility as much as
possible.
