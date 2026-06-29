# Phase 8 Progression And Core Mechanics Plan

Phase 8 turns character choices into mechanical differences.

The goal is not to build a full RPG skill tree immediately. The goal is to
create a stable progression foundation that the Agentic Runtime can use without
letting LLM narration grant unearned power.

Core rule:

```text
LLM may describe growth.
Rules decide growth.
Only structured progression state is real.
```

## Phase 8.1 Character Model Migration

Status: complete.

Implemented:

- added six future-facing attributes:
  - `physique`
  - `agility`
  - `insight`
  - `knowledge`
  - `will`
  - `communion`
- preserved old-save loading compatibility while moving new checks to attributes;
- added structured progression fields:
  - `class_level`
  - `faith_level`
  - `ascension_rank`
  - `revelation`
  - `favor`
  - `devotion`
  - `progression_skills`
  - `talents`
  - `prayers`
  - `burdens`
  - `progression_flags`
- added compatibility loading for older saves without progression data;
- exposed progression and attributes through `Character.to_public_dict()`;
- updated CLI status output to show core progression values.

Why this matters:

- saves, API responses, and future web UI now have a stable place for growth;
- old action logic keeps working while future checks migrate gradually;
- LLM cannot treat narrated growth as real unless these fields change.

## Phase 8.2 Minimal Class Skills

Status: complete.

Goal: make each class feel different in play.

Implemented:

- defined one Lv1 signature skill per class:
  - knight: `正面战斗基础`
  - mage: `异常解析基础`
  - operative: `潜行开锁基础`
  - ranger: `追踪侦察基础`
  - priest: `祷告仪式基础`
  - alchemist: `药剂鉴定基础`
- made class skills contribute a small bonus to matching world-mode checks;
- attached matched skill bonuses to roll results and check context;
- showed skill bonuses in player-facing dice output;
- exposed attributes, progression state, and skill affordances to the context
  pack for LLM providers;
- added natural 1 / natural 20 handling so skills cannot turn a catastrophic
  roll into a success.

Why this matters:

- class choice now changes actual adjudication without hard-coding every
  possible player action;
- LLM can describe how a skill helps, while Python still decides whether the
  check succeeds;
- future web/API clients can display skills and affordances from public state.

## Phase 8.3 Minimal Faith Talents And Prayers

Status: complete.

Goal: make faith choice matter.

Implemented:

- defined one Lv1 talent and one prayer per god;
- made talents provide small passive bonuses to matching world-mode checks;
- made prayers consume `favor` and provide a larger active bonus;
- attached talent/prayer bonuses and blocked prayers to roll results and check
  context;
- showed talent and prayer bonuses in player-facing dice output;
- exposed talent/prayer affordances to public progression state and context
  packs;
- connected hostile/restricted local church legality to prayer risk through
  suspicion pressure;
- preserved authority boundaries: prayers cannot grant unearned clues, items,
  travel, deaths, faction changes, endings, or growth rewards.

Why this matters:

- faith now changes how the player approaches a scene without becoming a free
  wish button;
- public prayer has social consequences in hostile or restricted religious
  environments;
- LLM can describe divine pressure, but Python still decides Favor cost,
  success, failure, and persistent effects.

## Phase 8.4 Generic Check System Migration

Status: complete.

Goal: move common world checks toward the six-attribute model.

Implemented:

- added shared world-mode check profiles that map `risk_type + check_attribute`
  to a primary six-attribute profile;
- added d20-style `attribute_modifier = (attribute - 10) // 2`;
- made the six-attribute modifier part of `行动修正`;
- attached `attribute_profile` and `attribute_modifier` to roll results and
  check context;
- made player-facing dice output show the six-attribute source, such as
  `属性：体魄 15 +2`;
- kept class skills, faith talents, prayers, context modifiers, and authority
  boundaries in the same check path.

Why this matters:

- six attributes now affect actual play without breaking older saves;
- early four-stat fields are old-save compatibility data, not the live check
  model;
- dice output remains readable while the internal model becomes more RPG-like.

## Phase 8.5 Ritual Advancement Slice

Status: complete.

Goal: make growth require story evidence and cost.

Implemented:

- added explicit advancement request detection for:
  - `class_level` 1 -> 2;
  - `faith_level` 1 -> 2;
  - `ascension_rank` 0 -> 1;
- added structured advancement evaluation with requirements, costs, rewards,
  and denial reasons;
- exposed `advancement_options` through public progression state and context
  packs;
- made class advancement consume `revelation` and grant one class-related
  attribute point;
- made faith advancement consume `revelation` and `favor`, then increase
  `devotion`;
- made first ascension require class level 2, faith level 2, enough
  `revelation`, enough `favor`, and add a burden;
- added structured rejection for unearned advancement, level change, and
  attribute change.

Why this matters:

- growth now has a rules-owned gate instead of being granted by narration;
- LLM can describe training, prayer, and ritual atmosphere, but only Python
  commits level, attribute, resource, and burden changes;
- future UI can show what advancement paths are available and what is still
  missing.

## Phase 8.6 Items And Relics Slice

Status: complete.

Goal: make items matter without letting them break authority rules.

Implemented:

- added `phase1_cli/items.py` as the rule-facing item layer while keeping
  inventory saved as a simple list of names;
- defined ordinary and consumable item categories now, with relic and cursed
  item categories reserved by the same interface for later phases;
- exposed player `item_affordances` through public state and Agentic Runtime
  context packs;
- added item bonuses to world-mode checks when the player explicitly invokes a
  carried item;
- added consumable item costs for checks, including inventory removal and
  `item_consumed` committed effects;
- added direct consumable use for recovery/cleansing items such as
  `镇静药剂` and `小瓶圣水`;
- kept generated temporary item proposals unable to grant inventory, clues, or
  state changes by narration alone.

Why this matters:

- items now matter mechanically without becoming free rewards;
- LLM can invent tempting objects, rumors, and props, but only committed
  inventory items can affect checks or state;
- future relics and cursed items can reuse the same effect/cost structure.

## Phase 8.7 Phase 8 Final Integration

Status: complete.

Goal: polish the growth and item loop into a coherent Phase 8 baseline.

Implemented:

- updated public status output to show six attributes, class skills, faith
  talents, prayers, item affordances, and advancement availability;
- updated help text with Phase 8 world-mode examples and rules;
- added a combined automated flow that uses class skill, faith talent, prayer,
  item effect, and faith advancement in sequence;
- updated project milestone/version text and Phase 8 documentation handoff.

Done:

- Phase 8 can be explained as one clean system instead of six separate slices.

## Phase 8 Completion

Phase 8 is complete as a baseline.

It does not mean the final progression system is finished. It means the project
now has working rule-owned interfaces for:

- six-attribute checks;
- class skill bonuses;
- faith talent bonuses;
- active prayers with `favor` cost;
- ritual advancement with requirements, costs, rewards, and denial reasons;
- item affordances, item bonuses, direct consumable use, and consumable costs.

Future phases can improve balance, add more content, and build UI around these
interfaces without letting LLM narration directly grant unearned rewards.
