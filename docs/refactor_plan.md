# Refactor Plan: Creative LLM, Stable Rules

This document corrects the long-term direction of Pantheon Age.

The project should not become a fixed rule game with LLM-flavored prose.
The goal is a rule-stabilized LLM Agent text adventure.

## Corrected Principle

```text
LLM creates possibilities.
Rules constrain authority, not imagination.
The rule system confirms reality.
Only validated structured state becomes game truth.
```

Chinese:

```text
LLM 负责扩展可能性。
规则限制的是改变现实的权限，而不是想象力。
规则系统负责裁定现实。
只有通过验证的结构化状态，才算真正发生。
```

## What The Rule Engine Should Do

The rule engine should not try to enumerate every possible story action.

It should provide:

- stable adjudication;
- mechanical consequences;
- resource and risk control;
- long-term progression gates;
- clue and secret release rules;
- permission boundaries for state changes;
- consistent standards that LLM output must obey.

The rule engine should answer questions like:

- Is this action possible here?
- What kind of check or cost is needed?
- What can success authorize?
- What can failure cost?
- Can this become persistent world truth?
- Is this result allowed by player knowledge and world state?

## What LLM Should Do

The LLM should generate:

- action candidates from natural-language input;
- scenes;
- NPCs;
- rumors;
- travel events;
- dialogue;
- atmospheric narration;
- local details;
- side content;
- possible complications.

The LLM should not directly decide:

- HP, SAN, money, items, clues, location, faction changes, deaths, endings;
- core world facts;
- hidden truth reveals;
- permanent memory commits.

## Content Authority Levels

LLM-generated content should be classified before it is used.

```text
flavor
  Atmospheric wording and sensory details.
  Can be generated freely, but must not contradict truth.

temporary
  Local scene details, unnamed NPCs, minor rumors.
  Can appear in narration but is not automatically persisted.

persistent
  Named NPCs, local facts, relationship changes, city events.
  Requires validation and explicit memory commit.

mechanical
  HP, SAN, money, inventory, clues, location, faction scores, endings.
  Must be authorized by deterministic rules.

secret
  Hidden truths, locked lore, unrevealed identities, core mysteries.
  Must not be revealed unless progression rules allow it.
```

## Target Runtime Flow

The long-term runtime should move toward this:

```text
player input
  -> RAG retrieves local/canon context
  -> LLM proposes ActionCandidate / SceneProposal / EventProposal
  -> validators check world canon, hidden info, and state permissions
  -> rule engine adjudicates mechanical authority and consequences
  -> memory layer decides what can persist
  -> RAG retrieves narration context
  -> LLM generates final NarrationProposal
  -> validators check final claims
  -> API / CLI / Web UI returns validated output
```

This is different from:

```text
fixed rule output -> LLM polish only
```

The LLM should generate possibilities before and after rule adjudication.
Rules and validators decide which possibilities have authority.

## Refactor Direction

### Step 1: Keep Existing Stable Layers

Do not rewrite Phase 1, Phase 2, or Phase 3.

Keep:

- `phase1_cli/` as the deterministic core and CLI demo;
- `phase2_api/` as the service/API layer;
- `phase3_persistence/` as the SQLite persistence layer;
- current tests as regression protection.

### Step 2: Expand LLM Runtime Contracts

Add proposal types beyond narration:

- `ActionCandidate`;
- `SceneProposal`;
- `EventProposal`;
- `NPCDialogueProposal`;
- `MemoryCandidate`.

Each proposal must declare:

- content text;
- intended authority level;
- claimed state changes;
- persistence request;
- hidden-info exposure risk;
- source provider.

### Step 3: Add Validation Layer

Create `validation/` before real LLM calls become powerful.

Validators should include:

- rule claim validator;
- lore validator;
- hidden information validator;
- reward validator;
- persistence permission validator;
- proposal schema validator.

### Step 4: Add Generic Rule Adjudication

The current `rule_engine.py` is scenario-specific.

Future rule logic should support generic checks:

- social check;
- stealth check;
- investigation check;
- travel risk check;
- occult analysis check;
- negotiation/bribe/intimidation check;
- danger escalation.

This lets LLM propose rich situations while the system adjudicates outcomes
with consistent standards.

### Step 5: Add Memory Commit Layer

Not every generated detail should become permanent.

Add a memory layer that can decide:

- do not persist;
- persist as session-only memory;
- persist as local world fact;
- persist as NPC relationship;
- persist as faction/world event.

### Step 6: Add RAG After Canon Is Split

RAG should retrieve relevant canon for:

- current country;
- current city;
- deity/church;
- class/archetype;
- tone guide;
- forbidden output rules;
- known local facts.

RAG provides context, not authority.

### Step 7: Add Real LLM Calls

Only after contracts, validators, and fallback are stable:

- implement real provider calls;
- require structured outputs;
- trace prompts, proposals, validation results, latency, and errors;
- keep tests network-free.

## Near-Term Phase 4 Adjustment

The next Phase 4 work should shift from "narration only" to "proposal runtime".

Recommended order:

1. Define `ActionCandidate`.
2. Define `SceneProposal` and `EventProposal`.
3. Add authority levels to proposals.
4. Add deterministic validators for proposal claims.
5. Keep `NarrationProposal` as final presentation, not the whole LLM system.

## What Not To Do

- Do not make the rule engine a list of every possible scene.
- Do not let LLM commit world truth directly.
- Do not let prompt text replace Python validators.
- Do not add real model calls before proposal validation is strong enough.
- Do not turn this into a fixed CLI game with prettier prose.
