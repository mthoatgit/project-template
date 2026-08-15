---
status: template
---

# <Project Name>

> **Template file.** Run `/init-project` to fill this in, or do it manually.
> Global rules live in `~/.claude/CLAUDE.md`; project-specific rules go here.
> Remove this banner and the YAML frontmatter once filled.
>
> **Two kinds of angle-bracket text below, and they are treated
> differently.** A `<placeholder>` sitting where a value belongs gets
> REPLACED with that value. A `<...>` block on its own line that explains
> what a section is for gets DELETED — it is guidance for whoever fills
> the file, not content for the finished one. Neither may survive into a
> real project; `init-verify.py` only catches a couple of them by name,
> so the rest is a reading job.
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

Once the tech stack is chosen (Stage 3), Claude MUST use these commands for build, test, run, and lint. Until then each line is a TBD stub — fill by replacing `<...>` placeholders (or the whole `TBD` line) with the real command:

```bash
# Build:    <build command>
# Test:     <test command>
# Run:      <run command>
# Lint/fmt: <lint command>
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

Tasks are executed by the orchestrator. Claude MUST use it during the implementation phase; Claude MUST NOT implement tasks manually.

```bash
orchestrator --tasks docs/tasks/ --test-cmd "<test-cmd>" --project-dir .
```

The orchestrator is **installed, not part of this repository** — there is no copy of it here and nothing to set up per project. Its source lives at `~/dev/orchestrator`, installed once per machine with `pip install -e`, and every project on the machine runs that same installation. If the command above is not found, the installation is missing rather than the project being broken; `~/dev/orchestrator/docs/consuming-the-orchestrator.md` says how to obtain it.
