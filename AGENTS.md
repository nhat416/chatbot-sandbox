# AGENTS.md

This file is the operating guide for AI coding agents working in this repository.

## 1) Purpose

Build and improve a simple FastAPI + OpenAI streaming chatbot sandbox with clear, small, safe changes.

Agent priorities (highest to lowest):

1. Correctness and safety
2. Keep behavior simple and predictable
3. Preserve project style and architecture
4. Keep changes minimal and easy to review
5. Improve docs/tests when behavior changes

## 2) Project Snapshot

- Backend: `app/main.py` (FastAPI app, `/chat`, `/health`, static mount)
- Frontend: `static/index.html` (single-file UI with inline CSS/JS)
- Env: `.env` (local only), template in `.env.example`
- Tooling: `uv`, Python 3.12+, FastAPI, OpenAI SDK

## 3) Spec-Driven Development Rules

Agents should treat a spec as the source of truth for implementation.

For non-trivial changes (new feature, behavior change, refactor with risk), use this flow:

1. Read existing behavior and constraints.
2. Create or update a short spec (see template below).
3. Implement in small steps that map to acceptance criteria.
4. Validate with tests/manual checks.
5. Update docs and this `AGENTS.md` if workflow/conventions changed.

Skip a full spec only for trivial edits (typos, tiny comment/doc fixes, obvious one-line bug fixes).

## 4) Spec Location and Naming

- Store specs in: `docs/specs/`
- File naming: `YYYY-MM-DD-short-kebab-title.md`
- If no spec exists for a non-trivial task, create one before major edits.

## 5) Feature Spec Template

Copy this template into a new file under `docs/specs/`.

```md
# <Feature or Change Title>

## Summary
One short paragraph describing what changes and why.

## Problem
What user/developer pain exists today?

## Goals
- Goal 1
- Goal 2

## Non-Goals
- Explicitly out-of-scope item 1

## Current Behavior
- What happens now (brief, concrete)

## Proposed Behavior
- What should happen after this change
- Include UX/API behavior details

## API / Data Contract Changes
- Request/response schema changes
- Validation rules
- Backward compatibility notes

## Edge Cases
- Case 1
- Case 2

## Acceptance Criteria
- [ ] Criterion 1 (testable)
- [ ] Criterion 2 (testable)

## Implementation Plan
1. Step 1
2. Step 2

## Validation Plan
- Automated checks:
  - `uv run ruff check .`
  - `uv run ruff format --check .` (if formatting standards apply)
- Manual checks:
  - Run app and verify affected user flow

## Risks and Mitigations
- Risk: ...
  - Mitigation: ...

## Rollback Plan
How to safely revert or disable if needed.
```

## 6) Coding Conventions for This Repo

- Keep backend logic straightforward in `app/main.py` unless complexity justifies splitting files.
- Maintain SSE behavior for `/chat`:
  - stream tokens as `data: <token>\n\n`
  - terminate with `data: [DONE]\n\n`
- Keep static mount last so API routes are not shadowed.
- Prefer explicit, readable code over clever abstractions.
- Preserve current dependency style in `pyproject.toml` unless change is justified in spec.

## 7) Safety and Security Rules

- Never commit secrets (`.env`, API keys, credentials).
- Do not log secrets or sensitive payloads.
- Treat external API failures as expected; handle gracefully.
- Avoid destructive file or git operations unless explicitly requested.

## 8) Validation Checklist (Before Finishing)

Run what applies to the scope of change:

1. `uv run ruff check .`
2. `uv run ruff format --check .` (or format the touched files)
3. `uv run fastapi dev app/main.py` and verify:
   - `GET /health` returns `{"status":"ok"}`
   - chat UI loads and streaming still works

If a check cannot run (missing tool/env), state that clearly and provide exact next command.

## 9) Pull Request Expectations

- Keep PRs focused and small.
- Reference the spec file in PR description for non-trivial changes.
- Include:
  - What changed
  - Why it changed
  - How it was validated
  - Any follow-up work

## 10) When to Update AGENTS.md

Update this file whenever any of these change:

- Development workflow or validation commands
- Project structure or architectural boundaries
- Coding conventions or safety rules
- Spec format/location requirements

Include AGENTS.md updates in the same PR as the change introducing the new rule.

## 11) Default Decision Policy for Agents

When requirements are ambiguous, choose the most conservative option that:

1. Preserves current behavior
2. Minimizes risk and code churn
3. Aligns with existing patterns in this repo

Escalate only when ambiguity materially changes behavior, security, or data handling.
