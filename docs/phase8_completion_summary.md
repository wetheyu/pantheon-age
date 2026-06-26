# Phase 8 Completion Summary

Phase 8 completes the first rule-owned progression and core mechanics baseline.

The goal was not to finish every class, prayer, relic, or balance detail. The
goal was to build reliable interfaces so future LLM-driven gameplay can be
imaginative without handing out unearned power.

Core rule:

```text
LLM may describe training, prayer, rituals, items, omens, and opportunities.
Python decides what changes state.
```

## Completed Capabilities

### Six Attributes

Characters now have six long-term attributes:

- Physique / 体魄
- Agility / 灵巧
- Insight / 洞察
- Knowledge / 知识
- Will / 意志
- Communion / 共鸣

World-mode checks map `risk_type + check_stat` into an attribute profile. The
attribute modifier is included in the visible roll output and `check_context`.

### Class Skills

Each class has one Lv1 signature skill:

- Knight / 骑士: 正面战斗基础
- Mage / 法师: 异常解析基础
- Operative / 密探: 潜行开锁基础
- Ranger / 游侠: 追踪侦察基础
- Priest / 牧师: 祷告仪式基础
- Alchemist / 炼金术士: 药剂鉴定基础

Skills can add small bonuses to matching world-mode checks, but cannot
guarantee success.

### Faith Talents And Prayers

Each god grants one passive talent and one active prayer baseline.

Talents are passive bonuses. Prayers are active bonuses that consume `favor`.
Religious legality can add suspicion pressure when the player invokes a
restricted or hostile faith in the wrong place.

### Ritual Advancement

Phase 8 implements the first advancement slice:

- class level 1 -> 2;
- faith level 1 -> 2;
- ascension rank 0 -> 1.

Advancement evaluates requirements, costs, rewards, and denial reasons before
state changes are committed. Failed advancement attempts are recorded as
attempts, but they do not grant levels, attributes, or burdens.

### Items And Consumables

Inventory is still saved as a simple list of names, but `phase1_cli/items.py`
now gives item names structured rule meaning.

Implemented item behavior:

- explicit item bonuses for world-mode checks;
- consumable item costs;
- direct consumable use for HP, SAN, and Corruption changes;
- player-facing `item_affordances`;
- context-pack item affordances for Agentic Runtime providers.

Generated temporary items still cannot directly enter the player inventory.

### Player-Facing Visibility

`状态` now shows:

- six attributes;
- class skills;
- faith talents;
- prayers;
- usable item affordances;
- advancement availability.

`帮助` now includes Phase 8 world-mode examples and explains how skills,
talents, prayers, items, and advancement interact with rules.

## Tests Added Or Expanded

Phase 8 is covered by tests for:

- save/load compatibility for new character fields;
- public response shapes for progression and item affordances;
- class skill bonuses;
- talent bonuses;
- prayer cost and blocked prayer behavior;
- hostile/restricted faith suspicion pressure;
- six-attribute check migration;
- advancement denial and commit paths;
- item bonuses and consumable costs;
- direct consumable item use;
- combined skill + talent + prayer + item + advancement flow.

## Current Limits

This is a baseline, not final balance.

Still future work:

- more class levels;
- more prayers and talents;
- richer relics and cursed items;
- deeper ritual materials;
- reward economy for Revelation, Favor, clues, money, and reputation;
- UI for showing options clearly;
- live playtest tuning with real LLM providers.

## Handoff To Phase 9

Phase 9 should focus on making the current game playable in a browser.

The UI should use the Phase 8 public state instead of inventing its own
progression model. In particular, it should surface:

- roll breakdown;
- current scene;
- inventory and item affordances;
- skills, talents, prayers;
- advancement options and missing requirements;
- committed effects versus temporary narration.

Phase 9 should not add a second rules engine.
