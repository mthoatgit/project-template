---
status: template
---

# <Project Name>

> **Template file.** Run `/init-project` to fill this in, or do it manually.
> Global rules live in `~/.claude/CLAUDE.md`; project-specific rules go here.
> Remove this banner and the YAML frontmatter once filled.
>
> **Writing style for this file:** see `~/.claude/rules/claude-md-style.md`.

## What this project is

<One or two sentences: what it does, who it's for. Mirror `docs/concept.md`.>

## Tech Stack

<Confirmed at Stage 3 (Architecture) of item 001's featurework lifecycle. Authoritative source: `docs/architecture/system-design.md` + ADRs.>

| Layer | Choice |
|---|---|
| <Language / runtime> | <e.g. Java 21> |
| <Framework> | <e.g. Spring Boot 3> |
| <Persistence> | <e.g. PostgreSQL> |
| <Build tool> | <e.g. Gradle> |

## Commands

Claude MUST use these commands for build, test, run, and lint:

```bash
# Build
<build command>
# Test
<test command>
# Run locally
<run command>
# Lint / format
<lint command>
```

## Verification

Claude MUST run the primary check before declaring a task done:

- <primary check, e.g. `mvn verify`>
- <optional secondary checks: type-check, lint, integration suite>

Scenario coverage: `docs/tests/README.md`.

## Dev Environment

<Non-obvious setup Claude cannot infer from the files:>

- <e.g. `docker-compose up -d` required for integration tests>
- <e.g. required env vars: `DATABASE_URL`, `API_KEY`>
- <e.g. `.envrc` managed by direnv>

## Code Layout

<Top-level directories and their purpose. Full structure: `docs/architecture/system-design.md`.>

- `<dir>/` — <purpose>
- `<dir>/` — <purpose>

## Conventions

<Project-specific rules. Use RFC 2119 style.>

- <e.g. All API responses MUST use the shared error envelope>
- <e.g. Database access MUST go through the repository layer>

## Gotchas

<Non-obvious behaviors that trip up new contributors:>

- <e.g. Integration tests require Docker running>

## Implementation

Claude MUST use the orchestrator during the implementation phase; Claude MUST NOT implement tasks manually.

```bash
python -m orchestrator --tasks docs/tasks/ --test-cmd "<test-cmd>" --project-dir .
```
