# Phase 5 Agentic Runtime Plan

Phase 5 turns the project from "LLM plugged into the old CLI" into a small but
real Agentic Runtime.

Core rule:

```text
LLM provides imagination.
Agents organize possibilities.
Programs validate, commit, remember, and audit.
```

## Phase 5 Scope

Phase 5 should not build the final open world all at once.

It should prove these capabilities in small steps:

- preserve open player intent;
- generate temporary scene/NPC/event/item candidates;
- propose rule adjudication;
- commit only validated state;
- curate memory candidates;
- narrate from confirmed results;
- support local providers and optional LLM-backed providers;
- keep tests deterministic by default.

## Stage Gate Workflow

Phase 5 is developed through explicit stage gates.

When the user says "推进下一个阶段", only implement the next stage marked
`next` in this document. Do not skip stages, merge multiple stages, or start
Phase 6 unless the user explicitly asks.

Each stage should end with:

- code and docs updated for that stage;
- focused tests added or updated when behavior changes;
- verification commands run;
- a short explanation of what changed, why it matters, and how to try it;
- the next stage marked clearly in this plan.

When the final Phase 5 stage is reached, first finish the stage, then do a full
Phase 5 integration pass: review architecture boundaries, remove stale docs,
align README / AGENTS / roadmap / system design, and summarize Phase 5 as a
complete version.

## Milestones

### v5.0.0 Agentic Runtime Baseline

Status: done.

- Add `agentic_runtime/`.
- Add `OpenActionProposal`, `RuleAdjudicationProposal`, `StateCommitProposal`,
  `MemoryCandidate`, `MemoryRetrievalResult`, and Phase 5 `NarrationProposal`.
- Add local Intent, Scene, Rule Arbiter, Memory Retriever, Memory Curator, Commit,
  and Narrator components.
- Add `PANTHEON_USE_AGENTIC_RUNTIME=1`.
- Prove `跳向前厅` can bridge to movement without patching old keywords.

### v5.1.0 Agent Provider Interfaces

Status: done.

- Add `agentic_runtime/providers.py`.
- Wrap local agents behind provider interfaces.
- Add `OpenAIIntentAgentProvider`.
- Add `prompts/open_action.md`.
- Add `PANTHEON_USE_AGENTIC_LLM=1`.
- Keep only Intent Agent LLM-backed at first.

### v5.2.0 Temporary World Agents

Status: done.

- Add local NPC Agent.
- Add local Event Agent.
- Add local Item Agent.
- Add proposal contracts and validators for NPC, event, and item candidates.
- Include generated temporary content in runtime trace and narration.
- Do not persist generated NPCs, events, or items yet.

### v5.3.0 Tutorial Scenario Split

Status: done.

- Keep the monastery as a tutorial/demo scenario.
- Define a separate world-mode entry point or flag.
- Make Phase 5 world-mode use generated temporary content more visibly.
- Keep Phase 1 parser/rule-engine useful for tutorial compatibility.
- Add `PANTHEON_GAME_MODE=world`.
- Add `world_action` so world-mode does not force open actions into the tutorial map.

### v5.3.1 Great Power Origin Selection

Status: done.

- Let world-mode players choose an origin country.
- Temporarily limit origin countries to the five great powers.
- Let each great power offer three fixed core cities as starting locations.
- Store origin country, identity, and starting city in public player state.
- Feed origin information into Agentic Runtime memory retrieval.

### v5.3.2 Playable Origin Selection

Status: done.

- Expand world-mode origin selection from five great powers to eight important countries.
- Add Noctia, Selemia, and Rosvia as playable origins.
- Keep three core city choices for each great power.
- Use one capital/unique city for each other important country at this stage.
- Keep origin information available to public state and Agentic Runtime memory.

### v5.3.3 Origin Culture Relations

Status: done.

- Add Ost ethnicity selection: 奥斯特人、佩斯塔人、波西恩人.
- Store origin ethnicity in public player state.
- Add local church legality context for each playable origin country.
- Feed origin ethnicity and church legality into Agentic Runtime memory retrieval.
- Document church legality, church-to-church relations, and the dynamic nation relation principle in the world bible.

### v5.3.4 Dynamic World Relations

Status: done.

- Keep church legality as initial social order.
- Stop treating nation-to-nation relations as fixed world bible canon.
- Add a dynamic nation relation interface for relation signals and snapshots.
- Let future agents propose relation changes from events, politics, factions,
  religion, rulers, trade, wars, and player actions.
- Require program validation before any relation change becomes persistent world memory.

### v5.4.0 LLM-backed World Agents

Status: done.

- Add OpenAI-backed NPC Agent.
- Add OpenAI-backed Event Agent.
- Add OpenAI-backed Item Agent.
- Keep local fallback providers.
- Add fake client tests before any live tests.
- Keep Rule Arbiter, Memory, Commit, and Narrator local until their authority
  boundaries are stable.
- Add per-agent fallback so one failed world-generation call does not stop the
  whole turn.

### v5.5.0 Memory Store Baseline

Status: done.

- Add a local memory store.
- Persist only validated memory candidates.
- Separate player-known, NPC-known, location, quest, and secret memory.
- Do not store raw LLM output as truth.
- Store memory records on `GameState.agentic_memory` so save/load can preserve
  the baseline memory store.

### v5.6.0 Memory-integrated Agentic Loop

Status: done.

- Connect memory retrieval and memory commit to the new memory store.
- Let validated memory candidates survive across turns.
- Keep secret memory hidden from player-facing narration and public state.
- Add tests for memory visibility and persistence boundaries.

### v5.7.0 Agentic World Mode Slice

Status: done.

- Run one small world-mode scene with generated NPCs, events, and items.
- Use state commit and memory curation.
- Keep deterministic boundaries for rewards, clues, items, and locations.
- Make the CLI experience visibly different from the old fixed tutorial loop.

### v5.8.0 Phase 5 Final Integration

Status: done.

- Review Phase 5 code paths end to end.
- Keep tutorial and world-mode behavior separated cleanly.
- Remove stale Phase 4 / Phase 5 wording from docs.
- Ensure README, AGENTS, system design, technical roadmap, and this plan all
  describe the same final Phase 5 architecture.
- Confirm tests cover the complete Phase 5 flow without live network calls.
- Produce the final Phase 5 summary before moving toward Phase 6.

Final summary: `docs/phase5_completion_summary.md`.

## Non-goals For Phase 5

- Full web UI.
- Full vector RAG.
- Full combat system rewrite.
- Full progression implementation.
- All agents calling LLM at once.
- Permanent open-world memory without validators.

## Completion Criteria

Phase 5 is complete when:

- CLI can run a small agentic world-mode slice. Done in `v5.7`.
- Open player intent is preserved. Done in `v5.0`.
- Temporary NPCs/events/items can be generated and validated. Done in `v5.2`.
- Rule adjudication and state commit are separated. Done in `v5.0`.
- Memory candidates are produced and validated. Done in `v5.5`.
- Optional LLM-backed agents have local fallback. Done in `v5.4`.
- Ordinary tests do not call the network or spend tokens. Verified in `v5.8`.

Phase 5 status: complete.
