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

Run this first:

```bash
./.venv/bin/python -m llm_runtime.smoke_test
```

Success looks like:

```text
Result: OpenAI action provider returned a candidate.
```

If it says fallback, missing key, model not found, timeout, or provider failed,
the real model path is not working yet.

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

and, when live unit tests are explicitly enabled:

```bash
./.venv/bin/python -m unittest tests.test_live_openai_provider
```

Codex should not read or print `.env`. It only needs the environment variables to
be loaded by the program.
