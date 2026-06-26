# Phase 7 Playtest Checklist

This checklist is the repeatable 20-minute manual playtest path for Pantheon Age.
It checks player experience, not exact LLM wording.

Run from the project root:

```bash
PANTHEON_GAME_MODE=world \
PANTHEON_USE_AGENTIC_LLM=1 \
PANTHEON_AGENTIC_TURN_DIRECTOR=1 \
PANTHEON_SHOW_RUNTIME=0 \
./.venv/bin/python -m phase1_cli.main
```

For a fast local-only sanity pass:

```bash
PANTHEON_GAME_MODE=world \
PANTHEON_USE_AGENTIC_LLM=0 \
PANTHEON_EMBEDDING_PROVIDER=local \
PANTHEON_CANON_RETRIEVAL=keyword \
./.venv/bin/python -m phase1_cli.main
```

## What Good Looks Like

- The game feels like a tabletop GM replying in a chat box.
- The player understands who they are, where they are, and what they can try.
- The narrator does not expose engineering words like validator, commit,
  rule_result, world slice, or temporary NPC.
- The player does not teleport unless travel is explicitly committed.
- High-risk actions show dice math and consequences.
- Success gives leverage, openings, pressure, or control, not automatic rewards.
- Death, permanent injury, clues, items, faction changes, and level-ups require
  explicit committed authority.
- Memory should make later turns feel aware of earlier actions.

## 20-Minute Manual Route

### 1. Opening

Create a world-mode character.

Suggested choices:

- country: 卢米埃
- city: 卢塞恩
- class: 密探
- god: 隐秘之神
- background: 调查记者

Expected:

- opening explains the world, origin, profession, faith, identity, and current
  situation;
- suggested actions are concrete enough to start playing;
- no debug report appears.

### 2. Low-Risk Opening Probe

Try:

```text
观察周围，确认今晚异常传闻的来源
```

Expected:

- narration stays in the current scene;
- no dice roll is required;
- no item, clue, location, or faction reward is granted.

### 3. Social Pressure

Try:

```text
说服附近报童谈谈昨夜的异常钟声
```

Expected:

- this may trigger an Intelligence-based social check;
- success should produce leverage or an opening;
- failure should produce caution, suspicion, or social pressure;
- exact prose can vary.

### 4. Investigation Without Teleport

Try:

```text
检查报社门口的失踪告示，看看有没有被人涂改
```

Expected:

- the narrator does not move you to a different city or unrelated place;
- it can describe visible signs, rumors, pressure, or questions;
- it should not hand out a confirmed clue unless the commit layer grants one.

### 5. Prayer / Occult Pressure

Try:

```text
向隐秘之神祈祷，请求遮蔽我的踪迹
```

Expected:

- this may trigger a Faith-based occult check;
- failure may cost SAN or increase Corruption only through committed state
  changes;
- the narrator should keep the result mysterious but readable.

### 6. Travel Request

Try:

```text
我准备乘船去维拉尔，询问航线和票据
```

Expected:

- the game should treat this as travel preparation, not instant arrival;
- current city remains 卢塞恩 unless a future travel system explicitly commits
  city movement;
- narration may discuss tickets, routes, contacts, and obstacles.

### 7. Violence Gate

Try:

```text
出手杀了拦路的守卫
```

Expected:

- a d20 check is shown;
- the output includes d20, stat, action modifier, DC, risk label, margin, and
  outcome tier;
- even on success, the guard is not automatically dead;
- the result should create advantage, pressure, resistance, alarm, or danger.

### 8. Memory Feel

After several turns, ask:

```text
回想一下我刚才已经做过什么
```

Expected:

- the game should acknowledge recent committed actions in a natural way;
- it should not reveal hidden facts or claim unearned conclusions.

## Known Acceptable Rough Edges

- Local-only mode is less imaginative than live LLM mode.
- Exact narrator wording can vary.
- Travel is still a request/preparation flow, not a complete journey system.
- Growth, inventory rewards, combat rounds, and clue economy are not final.
- Some DC and consequence balance will move to Phase 8.

## Automated Fixture

The local fixture mirrors the checklist without using real LLM calls:

```bash
PANTHEON_USE_AGENTIC_LLM=0 \
PANTHEON_USE_LLM=0 \
PANTHEON_EMBEDDING_PROVIDER=local \
PANTHEON_CANON_RETRIEVAL=keyword \
./.venv/bin/python -m unittest tests.test_playtest_fixtures
```

It checks stable safety properties instead of exact story prose.
