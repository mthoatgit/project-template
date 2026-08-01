---
status: template
---

# System Design

> **Template file.** Living overview of the current system. Written at
> Stage 3 (Architecture) of item 001 alongside ADR-0001, amended in
> place by any later item whose Stage 3 ADR changes the picture.
> Drop this block when filling in.
>
> **Loose shape.** Only Overview, Tech Stack, Component Overview, and
> Key Design Decisions are core (always present). Everything under
> "Optional sections" further down is OPTIONAL — keep the ones your
> project actually needs, delete the rest. Do not leave empty section
> headers; a placeholder header is worse than no section. See the
> `workflow-architecture` skill for the full artefact spec.

## Overview

<One-paragraph summary of the chosen architectural style — e.g.
"Modular monolith over microservices because …", "Single Python CLI
with local JSON storage", "Static site + edge worker" — and the
load-bearing trade-off behind it.>

---

## Tech Stack

<Quick reference for the chosen stack. Decided at Stage 3 (Architecture)
of item 001, recorded in `docs/adr/0001-tech-stack.md`. This table is
the at-a-glance mirror. Mandated/forbidden tech (a constraint, not a
choice) comes from `docs/concept.md` → Constraints.>

| Layer | Choice | ADR |
|---|---|---|
| <Language / runtime> | <e.g. Python 3.11> | 0001 |
| <Storage> | <e.g. JSON files under `~/.appname/`> | 0001 |
| <Build / packaging> | <e.g. hatch> | 0001 |

---

## Component Overview

```
<ASCII diagram of the major components and how they communicate.
Show external systems (DB, message bus, auth provider, filesystem)
at the boundaries. Even a CLI has components — argparse layer,
domain logic, persistence adapter.>
```

---

## Key Design Decisions

<Small design calls that were resolved during ripening and don't need
their own ADR. One line each. Larger or non-obvious decisions get a
dedicated ADR under `docs/adr/`.>

- **<Decision title>** — <one-line rationale>
- **<Decision title>** — <one-line rationale>

---

<!--
========================================================================
OPTIONAL SECTIONS BELOW.

Each has an "Add when..." hint. Keep the ones your project needs;
DELETE the rest (including their headers). A ghost header with no
body is worse than no section at all — the goal is a file that
faithfully describes THIS project, not a checklist of everything
architecture could involve.
========================================================================
-->

<!-- Add when: project is bigger than a single file; multiple modules -->
## Package / Module Structure

```
<root-package>
├── <module-1>
│   ├── <entry point / CLI / controller>
│   ├── <use cases / service>
│   ├── <persistence / adapter>
│   └── domain/<Entity>
├── <module-2>
│   └── ...
└── config
    └── <Cross-cutting configuration>
```

---

<!-- Add when: project has persistent state (DB, files, remote store) -->
## Data Model

```
<table-or-collection-or-json-schema>
  <field>, <field>, ...

<table-or-collection-or-json-schema>
  <field>, <field (FK / ref to ...)>, ...
```

---

<!-- Add when: system has async messaging -->
## Messaging / Integration

- **Topic / Queue:** `<name>`
- **Event:** `<EventName>`
  ```json
  {
    "<field>": "<type>",
    "<field>": "<type>"
  }
  ```
- **Producer:** `<class or service>`
- **Consumer:** `<class or service>`

---

<!-- Add when: system authenticates humans or services -->
## Authentication

<State the identity provider, the realm/tenant, the roles, and how
tokens are validated.>

---

<!-- Add when: system has a persistent schema that evolves -->
## Migrations

```
<migration-folder>/
  V1__<description>.sql
  V2__<description>.sql
```

---

<!-- Add when: local dev requires external services (DB, cache, queue) -->
## Local Dev / Compose Services

| Service | Image | Port |
|---|---|---|
| <name>  | <image:tag> | <port> |

---

<!-- Add when: system exposes a network API -->
## API Endpoints

| Method | Path | Description |
|---|---|---|
| <VERB> | <path> | <one-line summary> |

---

<!-- Add when: system has a user-facing UI (web/mobile/desktop) -->
## Rendering / UI Layer

<How templates, components, styling, and state management are
organized. Keep to the shape overview — details go in per-feature
docs.>
