---
status: template
---

# <Project Name>

> **Template file.** Replaced by `/init-project` with a minimal project README
> naming the project, one-line description, and pointing at `docs/` for the
> phased-workflow content. Remove this banner and the frontmatter when filled.

<One-line project description.>

Detailed docs live under [`docs/`](docs/) and follow the phased workflow. See
[`docs/workflow-overview.md`](docs/workflow-overview.md) for the diagram +
skill map and [`CLAUDE.md`](CLAUDE.md) for project-specific context.

## Implementation

Tasks in this project are implemented by the orchestrator:

```bash
orchestrator --tasks docs/tasks/ --test-cmd "<test-cmd>" --project-dir .
```

It is **installed, not part of this repository** — there is no copy of it here.
Its source lives at `~/dev/orchestrator`, installed once per machine, and every
project on the machine runs that same installation. If the command is not found,
the installation is missing rather than this project being broken — see
`~/dev/orchestrator/docs/consuming-the-orchestrator.md`.
