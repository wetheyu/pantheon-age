# Live LLM Testing Setup

This document explains how to configure local API credentials so live LLM tests
can be run from the project without exposing secrets in chat or Git.

## Safety Rules

- Never paste `OPENAI_API_KEY` into chat.
- Never commit `.env`.
- `.env.example` is safe to commit because it contains no real key.
- Do not print `.env` in terminal output.
- Live tests may spend API tokens, so they are opt-in.
- Codex may run live LLM smoke/tests only when the user explicitly allows live
  LLM testing in the current task.

## Local Setup

From the project root:

```bash
cp .env.example .env
```

Then open `.env` locally and fill in:

```text
OPENAI_API_KEY=your_real_key_here
PANTHEON_USE_LLM=1
PANTHEON_OPENAI_MODEL=gpt5.5
```

Use a model that your API key actually has access to. Override
`PANTHEON_OPENAI_MODEL` locally if your account or endpoint uses a different
model name.

## OpenAI-Compatible Local Providers

Phase 10.5 supports official OpenAI and local OpenAI-compatible endpoints
through the same provider boundary. To use a local server, keep the game logic
unchanged and configure only `.env`.

Ollama example:

```text
OPENAI_API_KEY=local
PANTHEON_OPENAI_PROVIDER=ollama
PANTHEON_OPENAI_BASE_URL=http://localhost:11434/v1
PANTHEON_OPENAI_MODEL=your-local-model
```

LM Studio example:

```text
OPENAI_API_KEY=local
PANTHEON_OPENAI_PROVIDER=lm_studio
PANTHEON_OPENAI_BASE_URL=http://localhost:1234/v1
PANTHEON_OPENAI_MODEL=your-local-model
```

vLLM example:

```text
OPENAI_API_KEY=local
PANTHEON_OPENAI_PROVIDER=vllm
PANTHEON_OPENAI_BASE_URL=http://localhost:8000/v1
PANTHEON_OPENAI_MODEL=your-local-model
```

Notes:

- Leave `PANTHEON_OPENAI_BASE_URL` empty for official OpenAI.
- Custom local endpoints use the chat-completions JSON path, so the local
  server does not need to support OpenAI Responses API.
- Local compatible servers often still require a placeholder `OPENAI_API_KEY`.
- Local models may be weaker at strict structured JSON. If smoke tests fail
  with parsing or schema errors, try a stronger instruct model, reduce output
  length, or use the official provider for important playtests.
- Provider switching must not bypass validators, dice, state commit, or memory
  commit rules.

## Smoke Test

Run the older Phase 4 provider smoke test first:

```bash
./.venv/bin/python -m llm_runtime.smoke_test
```

Success looks like:

```text
Result: OpenAI action provider returned a candidate.
```

If it says fallback, missing key, model not found, timeout, or provider failed,
the real model path is not working yet.

If the Agentic Runtime smoke test reports invalid JSON or EOF while parsing a
structured response, increase `PANTHEON_OPENAI_MAX_OUTPUT_TOKENS`. The Turn
Director returns intent, adjudication, scene, NPC, event, item, and narration in
one structured payload, so live play needs more output budget than a single
short answer.

For the current Agentic Runtime path, use:

```bash
./.venv/bin/python -m agentic_runtime.smoke_test
```

This prints:

- runtime branch: `local`, `creative_gm`, `turn_director`, `turn_director_fallback_local`,
  `legacy_world_bundle`, or `full_multi_agent`;
- provider endpoint summary: official OpenAI or custom OpenAI-compatible endpoint;
- total elapsed time;
- per-step timings;
- provider reason;
- narration preview.

It only calls OpenAI when `.env` enables `PANTHEON_USE_AGENTIC_LLM=1` and a real
`OPENAI_API_KEY` is configured.

For the recommended high-freedom live play path, set:

```text
PANTHEON_PLAY_PROFILE=fast
PANTHEON_CREATIVE_GM_MODE=1
PANTHEON_AGENTIC_TURN_DIRECTOR=1
PANTHEON_AGENTIC_FULL_LLM=0
```

In this mode, the LLM acts as the player-facing GM first. Python still owns
memory, validation, dice, and state commit.

Phase 10.4 adds four runtime profiles:

```text
local   = offline local providers, zero API cost
fast    = recommended live play, one Creative GM call
quality = more context/output budget for important scenes
debug   = live play with runtime output enabled
```

Profile smoke commands:

```bash
env PANTHEON_PLAY_PROFILE=local ./.venv/bin/python -m agentic_runtime.smoke_test
env PANTHEON_PLAY_PROFILE=fast ./.venv/bin/python -m agentic_runtime.smoke_test
env PANTHEON_PLAY_PROFILE=quality ./.venv/bin/python -m agentic_runtime.smoke_test
env PANTHEON_PLAY_PROFILE=debug ./.venv/bin/python -m agentic_runtime.smoke_test
```

The smoke output includes the runtime branch, slowest steps, profile budget
status, and speed advice. In the current live path, most latency usually comes
from the single OpenAI provider call rather than Python-side validation,
memory, dice, or state commit.

## Live Unit Tests

To let optional live LLM unit tests run, set this in `.env`:

```text
PANTHEON_RUN_LIVE_LLM_TESTS=1
PANTHEON_USE_AGENTIC_LLM=1
```

Older Phase 4 provider test:

```bash
./.venv/bin/python -m unittest tests.test_live_openai_provider
```

Current Agentic Runtime live test:

```bash
./.venv/bin/python -m unittest tests.test_live_agentic_runtime
```

The default test suite still skips these tests unless live flags and
`OPENAI_API_KEY` are present, so normal tests do not spend tokens by accident.

## CLI With Real LLM

```bash
./.venv/bin/python -m phase1_cli.main
```

Because `providers.py` loads `.env` automatically, you do not need to put the API
key directly into the command.

## Codex Workflow

When a task touches LLM provider behavior, live LLM behavior, or prompt/runtime
changes, Codex can run:

```bash
./.venv/bin/python -m llm_runtime.smoke_test
```

For Agentic Runtime latency or branch checks, Codex can run:

```bash
./.venv/bin/python -m agentic_runtime.smoke_test
```

and, when live unit tests are explicitly enabled:

```bash
./.venv/bin/python -m unittest tests.test_live_openai_provider
./.venv/bin/python -m unittest tests.test_live_agentic_runtime
```

Codex should not read or print `.env`. It only needs the environment variables to
be loaded by the program.
