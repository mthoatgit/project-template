---
status: template
---

# <Project Name>

> **Template file.** Run `/init-project` to fill this in, or do it
> manually. This file gives Claude project-specific context; the phased
> workflow rules live in the global `~/.claude/CLAUDE.md`. Remove this
> banner and the YAML frontmatter once filled.

## What this project is

<One or two sentences: what it does, who it's for. Mirror docs/concept.md
once that exists.>

## Tech Stack

<Confirmed during the Architecture Phase (Phase 2). This table is a quick
reference for Claude — the authoritative decision lives in
docs/architecture/system-design.md (and ADRs). Keep them in sync. Leave
as TBD until Phase 2 if not yet decided.>

| Layer | Choice |
|---|---|
| <Language / runtime> | <e.g. Java 21> |
| <Framework> | <e.g. Spring Boot 3> |
| <Persistence> | <e.g. PostgreSQL> |
| <Build tool> | <e.g. Gradle> |

## Commands

<How to build, test, run, lint. These are the commands Claude should use.
Fill in as the project takes shape.>

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

## Code Layout

<Top-level directories and their purpose. Point to
docs/architecture/system-design.md for the full structure.>

- `<dir>/` — <purpose>
- `<dir>/` — <purpose>

## Conventions

<Project-specific conventions beyond the global workflow rules.>

- <e.g. All API responses use a shared error envelope>
- <e.g. Database access only through the repository layer>

## Gotchas

<Non-obvious things that trip up a new contributor (human or AI).>

- <e.g. Integration tests require Docker running>
