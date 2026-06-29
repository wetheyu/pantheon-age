# Development Setup

This document is the repeatable local setup guide for Pantheon Age.

## 1. Python Environment

From the project root:

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
```

Run a safe local check:

```bash
./.venv/bin/python scripts/dev.py check
```

This command compiles Python files and runs the offline unit test suite with
live LLM and live embedding calls disabled.

## 2. Environment File

Create a local `.env`:

```bash
cp .env.example .env
```

Never commit `.env`.

Useful profiles:

```text
PANTHEON_PLAY_PROFILE=local    # local fallback path, zero API cost
PANTHEON_PLAY_PROFILE=fast     # recommended live play path
PANTHEON_PLAY_PROFILE=quality  # more context/output for important playtests
PANTHEON_PLAY_PROFILE=debug    # live path with runtime/debug output
```

Official OpenAI:

```text
OPENAI_API_KEY=your_key
PANTHEON_OPENAI_PROVIDER=openai
PANTHEON_OPENAI_BASE_URL=
PANTHEON_OPENAI_MODEL=gpt-4o-mini
```

OpenAI-compatible local endpoint:

```text
OPENAI_API_KEY=local
PANTHEON_OPENAI_PROVIDER=ollama
PANTHEON_OPENAI_BASE_URL=http://localhost:11434/v1
PANTHEON_OPENAI_MODEL=your-local-model
```

Local providers and official OpenAI share the same validators, dice, state
commit, and memory commit boundaries.

## 3. Common Commands

Doctor:

```bash
./.venv/bin/python scripts/dev.py doctor
```

CLI:

```bash
./.venv/bin/python scripts/dev.py cli
```

API:

```bash
./.venv/bin/python scripts/dev.py api
```

Local Agentic Runtime smoke:

```bash
./.venv/bin/python scripts/dev.py agentic-smoke
```

Final demo smoke:

```bash
./.venv/bin/python scripts/dev.py final-demo
```

Web install:

```bash
./.venv/bin/python scripts/dev.py web-install
```

Web dev server:

```bash
./.venv/bin/python scripts/dev.py web-dev
```

Web build:

```bash
./.venv/bin/python scripts/dev.py web-build
```

Web API smoke:

```bash
./.venv/bin/python scripts/dev.py web-smoke
```

The API must be running before `web-smoke`.

## 4. Docker Decision

Docker Compose is intentionally deferred for now.

Reason:

- the main development loop is still CLI/API/Web on one machine;
- SQLite does not require a separate database service;
- local model runtimes differ widely between Ollama, LM Studio, vLLM, and cloud
  OpenAI-compatible endpoints;
- a premature Docker setup would add maintenance cost before the final demo path
  is locked.

Add Docker later only if the final demo needs one-command API + Web startup or a
repeatable portfolio deployment target.

## 5. Local Runtime Files

These should stay untracked:

- `.env` and local env variants;
- `.venv/`;
- `saves/*.json`;
- `data/*.sqlite3`, `data/*.sqlite3-*`, `data/*.db`, and local logs;
- Python caches and coverage output;
- `web_ui/node_modules/`, `web_ui/dist/`, `web_ui/.env.local`, and Vite caches.

## 6. Before Publishing To GitHub

Run the local checks:

```bash
./.venv/bin/python scripts/dev.py check
cd web_ui
npm run build
```

Confirm private/runtime files are ignored:

```bash
git check-ignore -v .env .local_notes/project_interview_guide.md data/pantheon_age.sqlite3 web_ui/dist/index.html
```

See [github_release_checklist.md](github_release_checklist.md) for the full
publish checklist.
