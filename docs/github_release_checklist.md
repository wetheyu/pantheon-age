# GitHub Release Checklist

Use this checklist before publishing or updating the GitHub repository.

## Keep Private Files Local

These files and folders are intentionally ignored and should not be committed:

- `.env` and local env variants;
- `.venv/`;
- `.local_notes/`;
- `data/*.sqlite3`, `data/*.db`, and local data logs;
- `saves/*.json`;
- `web_ui/node_modules/`;
- `web_ui/dist/`;
- `web_ui/.env.local`;
- Python, TypeScript, coverage, and cache output.

Quick check:

```bash
git check-ignore -v .env .local_notes/project_interview_guide.md data/pantheon_age.sqlite3 web_ui/dist/index.html
```

## Verify The Project

From the project root:

```bash
./.venv/bin/python scripts/dev.py check
```

From `web_ui/`:

```bash
npm run build
```

Optional, when the API is already running:

```bash
npm run smoke:api
```

## Public Docs To Skim

- `README.md`: project pitch, quick run, API/Web usage, limitations.
- `docs/README.md`: documentation map.
- `docs/project_architecture.md`: current architecture and module boundaries.
- `docs/final_demo.md`: 5-10 minute portfolio demo path.
- `docs/dev_setup.md`: local setup and runtime files.
- `docs/progression_design.md`: six-attribute progression model.

## Current Public Story

When describing the project, emphasize:

- LLMs create possibilities, but Python commits reality.
- Agentic Runtime separates proposal, validation, dice, state commit, memory,
  and narration.
- World-mode checks use six attributes: `physique`, `agility`, `insight`,
  `knowledge`, `will`, and `communion`.
- The browser UI is a playtest client and does not duplicate game rules.
- Normal tests are offline and zero API cost; live LLM tests are opt-in.

## Suggested Commit Scope

For a public upload, prefer one coherent commit that includes:

- source code;
- prompts;
- tests;
- README and docs;
- `.env.example`;
- `.gitignore`.

Do not include local generated runtime data, local saves, API keys, private
interview notes, or frontend build output.
