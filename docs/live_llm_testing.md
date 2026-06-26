# Live LLM Testing Setup

This document explains how to configure local API credentials so live LLM tests
can be run from the project without exposing secrets in chat or Git.

## Safety Rules

- Never paste `OPENAI_API_KEY` into chat.
- Never commit `.env`.
- `.env.example` is safe to commit because it contains no real key.
- Do not print `.env` in terminal output.
- Live tests may spend API tokens, so they are opt-in.

## Local Setup

From the project root:

```bash
cp .env.example .env
```

Then open `.env` locally and fill in:

```text
OPENAI_API_KEY=your_real_key_here
PANTHEON_USE_LLM=1
PANTHEON_OPENAI_MODEL=gpt-4o-mini
```

Use a model that your API key actually has access to. If `gpt-5.5` is available
to your account, you can set:

```text
PANTHEON_OPENAI_MODEL=gpt-5.5
```

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
- total elapsed time;
- per-step timings;
- provider reason;
- narration preview.

It only calls OpenAI when `.env` enables `PANTHEON_USE_AGENTIC_LLM=1` and a real
`OPENAI_API_KEY` is configured.

For the recommended high-freedom live play path, set:

```text
PANTHEON_CREATIVE_GM_MODE=1
PANTHEON_AGENTIC_TURN_DIRECTOR=1
PANTHEON_AGENTIC_FULL_LLM=0
```

In this mode, the LLM acts as the player-facing GM first. Python still owns
memory, validation, dice, and state commit.

## Live Unit Test

To let the optional live LLM unit test run, set this in `.env`:

```text
PANTHEON_RUN_LIVE_LLM_TESTS=1
```

Then run:

```bash
./.venv/bin/python -m unittest tests.test_live_openai_provider
```

The default test suite still skips this test unless `PANTHEON_RUN_LIVE_LLM_TESTS`
is enabled, so normal tests do not spend tokens by accident.

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
```

Codex should not read or print `.env`. It only needs the environment variables to
be loaded by the program.
