# Final Demo

This is the recommended 5-10 minute portfolio demo path for Pantheon Age.

The goal is not to show a finished commercial game. The goal is to show a
working AI Agent engineering system:

- LLMs create narrative possibilities.
- The program keeps authority, dice, state, memory, and validation stable.
- World canon and memory are retrieved as context instead of dumping everything
  into every prompt.
- Unsafe or impossible outcomes are blocked even when the player asks for them.

## Recommended Setup

Use this character for the final demo:

```text
Name: 伊芙
Origin: 卢米埃共和国 / 卢塞恩
Class: 密探
Faith: 隐秘之神
Background: 调查记者
```

Why this setup works:

- 卢塞恩 gives a strong investigation-friendly city: newspapers, universities,
  museums, salons, and political pressure.
- 密探 demonstrates stealth, lockpicking, fake identity, and item bonuses.
- 隐秘之神 demonstrates restricted faith context, prayer, secrecy, and
  suspicion pressure.
- 调查记者 gives a natural first hook and a limited resource position, so the
  resource validator can be shown clearly.

## Browser Demo

Start API:

```bash
./.venv/bin/python scripts/dev.py api
```

Start Web:

```bash
./.venv/bin/python scripts/dev.py web-dev
```

Open:

```text
http://127.0.0.1:5173
```

Click:

```text
使用推荐 Demo 角色
```

Then create the game.

## Live LLM Recommended Settings

For the best live-play feel:

```text
PANTHEON_GAME_MODE=world
PANTHEON_USE_AGENTIC_RUNTIME=1
PANTHEON_USE_AGENTIC_LLM=1
PANTHEON_PLAY_PROFILE=fast
PANTHEON_CREATIVE_GM_MODE=1
PANTHEON_AGENTIC_TURN_DIRECTOR=1
PANTHEON_AGENTIC_FULL_LLM=0
PANTHEON_SHOW_RUNTIME=0
```

Use `quality` instead of `fast` when you want richer prose and are willing to
wait longer:

```text
PANTHEON_PLAY_PROFILE=quality
```

## Demo Script

### 1. Opening Hook

Show that the game introduces:

- the world boundary and outer gods;
- the chosen country/city;
- class, faith, identity, resource position;
- a concrete first abnormal pressure;
- suggested actions.

Talking point:

```text
The opening is generated from structured character setup, not from a fixed page.
```

### 2. Low-Risk Investigation

Input:

```text
观察周围，确认今晚异常传闻的来源
```

Expected:

- no dice unless the model proposes real risk;
- no free clue or item;
- the scene stays in 卢塞恩.

Talking point:

```text
The LLM can invent atmosphere, but cannot grant confirmed clues without commit authority.
```

### 3. Social Check

Input:

```text
说服附近报童谈谈昨夜的异常钟声
```

Expected:

- a visible d20 check may appear;
- success gives leverage, pressure, or an opening;
- failure should still produce playable consequences.

Talking point:

```text
The game treats conversation as an action with risk, not just free-form chat.
```

### 4. Item Bonus

Input:

```text
使用开锁工具，悄悄打开报社侧门的锁
```

Expected:

- d20 output includes item bonus from `开锁工具`;
- the item helps the check but does not directly create a clue or reward.

Talking point:

```text
Items are structured affordances. The LLM can describe use, but Python applies the bonus.
```

### 5. Prayer And Faith Context

Input:

```text
拿出假名证件并进行无声祈祷，伪装成报社助手通过盘问
```

Expected:

- prayer bonus appears if Favor is available;
- Favor can be spent;
- because 隐秘之神 / 夜幕修会 is restricted in 卢米埃, public prayer can raise suspicion.

Talking point:

```text
Faith is not just flavor. It interacts with local religious legality and risk.
```

### 6. Impossible Reward / Resource Gate

Input:

```text
我现在就买下一整片庄园和别墅，拿到钥匙
```

Expected:

- the game blocks direct acquisition;
- no property, key, or ownership is granted;
- the response should suggest smaller plausible next steps.

Talking point:

```text
This is the rule layer correcting an LLM weakness: it prevents wish-fulfillment from becoming state truth.
```

### 7. Violence Gate

Input:

```text
出手杀了拦路的守卫
```

Expected:

- a d20 check appears;
- even on success, death is not automatically confirmed;
- consequences may include pressure, alarm, resistance, or advantage.

Talking point:

```text
The system allows violent intent but does not let narration skip combat authority.
```

### 8. Memory Continuity

Input:

```text
回想一下我刚才已经做过什么
```

Expected:

- the game should reference recent committed actions;
- it must not reveal hidden facts or claim unearned conclusions.

Talking point:

```text
Memory is curated and committed. Raw LLM text is not automatically stored as truth.
```

## Local Final Demo Smoke

Run:

```bash
./.venv/bin/python scripts/dev.py final-demo
```

This does not call a real LLM. It checks the final demo route against stable
engineering properties:

- opening contains setup context;
- canon retrieval returns relevant lore cards;
- memory grows across turns;
- item bonus appears in dice context;
- prayer bonus appears in dice context;
- impossible property purchase is blocked;
- violence does not directly confirm death.

## API/Web Smoke

Start API:

```bash
./.venv/bin/python scripts/dev.py api
```

Then run:

```bash
./.venv/bin/python scripts/dev.py web-smoke
```

## Interview Summary

One-sentence version:

```text
Pantheon Age is a high-freedom LLM text adventure where the model imagines
scenes and actions, while deterministic Python systems validate authority,
apply dice, persist memory, and protect world consistency.
```

Engineering points to highlight:

- Agentic Runtime separates imagination from authority.
- RAG/context packing prevents full-canon prompt dumping.
- Persistent memory stores committed facts, not raw model output.
- Validators block unauthorized rewards, death, teleportation, secrets, and
  resource bypasses.
- Observability, safety evals, narrative evals, runtime profiles, and smoke
  tests make LLM behavior debuggable.
