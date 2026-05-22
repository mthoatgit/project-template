---
status: template
---

# System Design

> **Template file.** Produced and maintained during the Architecture
> Phase. Replace every `<PLACEHOLDER>` and drop this block when filling
> the file in for a real project. Sections that don't apply should be
> deleted, not left empty.

## Overview

<One-paragraph summary of the chosen architectural style — e.g.
"Modular monolith over microservices because …" — and the load-bearing
trade-off behind it.>

---

## Tech Stack

<Quick reference for the chosen stack. This is where the tech stack is
decided (Phase 2) — NOT in the requirements. For a non-trivial choice,
record the decision, rationale, and rejected alternatives in
`docs/adr/0001-tech-stack.md` and keep this table as the at-a-glance
mirror. Mandated/forbidden tech (a constraint, not a choice) comes from
`docs/concept.md` → Constraints.>

| Layer | Choice | ADR |
|---|---|---|
| <Language / runtime> | <e.g. Java 21> | <0001> |
| <Framework> | <e.g. Spring Boot 3> | <0001> |
| <Persistence> | <e.g. PostgreSQL> | <0001> |
| <Build tool> | <e.g. Gradle> | <0001> |

---

## Component Overview

```
<ASCII diagram of the major components and how they communicate.
Show external systems (DB, message bus, auth provider) at the bottom.>
```

---

## Package / Module Structure

```
<root-package>
├── <module-1>
│   ├── <Controller / API entry>
│   ├── <Service / use cases>
│   ├── <Repository / persistence>
│   └── domain/<Entity>
├── <module-2>
│   └── ...
└── config
    └── <Cross-cutting configuration classes>
```

---

## Data Model

```
<table-or-collection-name>
  <column>, <column>, ...

<table-or-collection-name>
  <column>, <column (FK to ...)>, ...
```

---

## Messaging / Integration

<Drop this section if the system has no async messaging.>

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

## Authentication

<Drop or replace if not applicable. State the identity provider, the
realm/tenant, the roles, and how tokens are validated.>

---

## Migrations

```
<migration-folder>/
  V1__<description>.sql
  V2__<description>.sql
```

---

## Local Dev / Compose Services

| Service | Image | Port |
|---|---|---|
| <name>  | <image:tag> | <port> |

---

## API Endpoints (planned)

| Method | Path | Description |
|---|---|---|
| <VERB> | <path> | <one-line summary> |

---

## Key Design Decisions

- **<Decision title>** — <one-line rationale>
- **<Decision title>** — <one-line rationale>

> Larger or more controversial decisions should also get a dedicated ADR
> under `docs/adr/`.
