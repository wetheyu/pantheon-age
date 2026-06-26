# Pantheon Age Web UI

Phase 9.6 browser playtest client for Pantheon Age.

This app should consume FastAPI responses. It must not duplicate game rules,
state mutation, dice logic, validators, memory commit rules, or Agentic Runtime
logic in frontend code.

## Run

Start the API from the project root:

```bash
./.venv/bin/uvicorn phase2_api.main:app
```

Start the web app:

```bash
cd web_ui
npm install
npm run dev
```

Open:

```text
http://127.0.0.1:5173
```

## API Config

Default API base URL:

```text
http://127.0.0.1:8000
```

Override it in `web_ui/.env.local`:

```text
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## Current Scope

- Read `/health`, `/classes`, `/gods`, and `/origins`.
- Show backend connection status.
- Create a world-mode game through `POST /games`.
- Display returned `game_id`, public first-scene state, and opening narration.
- Submit player actions through `POST /games/{game_id}/actions`.
- Render player messages, host story responses, loading state, and lightweight
  mechanics summaries.
- Show read-only character/world panels for identity, HP/SAN, attributes,
  progression, inventory, clues, and current scene.
- Show opening action suggestions and allow starting a new character from the
  play surface.
- Handle game-over state by disabling further action submission.

## Smoke Check

Start the API first, then run:

```bash
npm run smoke:api
```

The smoke script checks the main browser-facing API path without launching a
browser.

Phase 9 Web/API product baseline is complete. Further work belongs to Phase 10
observability, evals, packaging, and final experience optimization.
