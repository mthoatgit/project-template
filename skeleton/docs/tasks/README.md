# Work Items

Task and bug files live flat directly under `docs/tasks/`. There are no per-Epic subdirectories and no `cross/` subdirectory — Epic ownership is expressed via each file's `**Epic:**` header field, not by folder placement.

## Layout

```
docs/tasks/
├── README.md                   ← this file
├── index.md                    ← merged work-item index (tasks + bugs) — orchestrator SoT
├── _TEMPLATE_TASK.md
├── _TEMPLATE_BUG.md
├── TASK-<NNNN>-<slug>.md       ← task work items
└── BUG-<NNNN>-<slug>.md        ← bug work items
```

## Filename convention

- Tasks: `TASK-<NNNN>-<slug>.md`
- Bugs: `BUG-<NNNN>-<slug>.md`
- `<NNNN>` is a global four-digit zero-padded counter **shared across tasks and bugs** — a task ID and a bug ID never share the same number. Numbering follows filing order.
- `<slug>` is a short kebab-case topical keyword.

## Epic ownership

Every task and bug file carries an `**Epic:**` header field. The value MUST be either an Epic ID (e.g. `E1-<slug>`) or the literal `none` — the latter for cross-Epic or project-wide work items that do not sit under any single Epic. `docs/tasks/index.md`'s `Epic` column mirrors this field and is the primary Epic-navigation surface.

## Templates

- [`_TEMPLATE_TASK.md`](_TEMPLATE_TASK.md) — canonical structure for task files.
- [`_TEMPLATE_BUG.md`](_TEMPLATE_BUG.md) — canonical structure for bug files.

Both templates carry `status: template` frontmatter and inline banner per `~/.claude/rules/templates.md`; remove both when filling with real content.
