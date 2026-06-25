# Pantheon Age Documentation

This folder contains the project design, world canon, runtime rules, phase
summaries, and future development plans.

Use this file as the documentation entry point.

## Source Of Truth

Read these first:

1. [../AGENTS.md](../AGENTS.md) - engineering rules, architecture boundaries, test commands, and workflow constraints.
2. [phase1_6_architecture_summary.md](phase1_6_architecture_summary.md) - current baseline after Phase 6.
3. [agentic_runtime_architecture.md](agentic_runtime_architecture.md) - long-term multi-agent runtime model.
4. [future_phase_plan.md](future_phase_plan.md) - Phase 7-10 execution plan.
5. [world_bible.md](world_bible.md) - readable world overview.

## Current Architecture

- [phase1_6_architecture_summary.md](phase1_6_architecture_summary.md): consolidated architecture baseline.
- [agentic_runtime_architecture.md](agentic_runtime_architecture.md): target Agentic Runtime responsibilities and boundaries.
- [llm_runtime_design.md](llm_runtime_design.md): LLM proposal, validation, commit, and narration rules.
- [system_design.md](system_design.md): broader phase-by-phase architecture notes.
- [technical_roadmap.md](technical_roadmap.md): long-term technology options and technical areas.

## World And Canon

- [world_bible.md](world_bible.md): main world overview.
- [canon/](canon/README.md): retrievable canon corpus for RAG.
- [progression_design.md](progression_design.md): attributes, class levels, faith levels, rituals, items, and costs.
- [tone_guide.md](tone_guide.md): narration tone and style guide.
- [forbidden_outputs.md](forbidden_outputs.md): LLM authority boundaries and forbidden claims.
- [inspiration_notes.md](inspiration_notes.md): high-level inspirations and originality boundaries.
- [rag_seed_cards.md](rag_seed_cards.md): compact fallback RAG cards.

## Phase Records

Completed or historical phase documents:

- [phase2_api_plan.md](phase2_api_plan.md): FastAPI migration plan.
- [phase4_llm_runtime_plan.md](phase4_llm_runtime_plan.md): structured LLM runtime plan.
- [phase5_agentic_runtime_plan.md](phase5_agentic_runtime_plan.md): Phase 5 staged build plan.
- [phase5_completion_summary.md](phase5_completion_summary.md): Phase 5 completion summary.
- [phase6_world_memory_plan.md](phase6_world_memory_plan.md): Phase 6 staged build plan.
- [phase6_completion_summary.md](phase6_completion_summary.md): Phase 6 completion summary.

Future execution:

- [future_phase_plan.md](future_phase_plan.md): Phase 7 minimum playable experience, Phase 8 progression, Phase 9 web/API product experience, and Phase 10 engineering quality.

## Runtime And Testing

- [live_llm_testing.md](live_llm_testing.md): safe `.env` setup and opt-in live LLM tests.

Normal automated tests should remain local and network-free. Live LLM and
embedding calls must stay opt-in through environment variables.

## Maintenance Rules

- Keep world facts in `world_bible.md` or `docs/canon/`.
- Keep engineering rules in `AGENTS.md`.
- Keep future implementation work in `future_phase_plan.md`.
- Keep detailed phase history in phase-specific plan or summary files.
- Avoid duplicating the same architecture rule across many documents.
