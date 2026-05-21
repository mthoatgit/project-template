# project-template

Starter scaffolding for new projects. Combines the phased AI-driven
workflow conventions, Claude Code settings, and the GitHub Actions
stubs that delegate to [mthoatgit/workflows](https://github.com/mthoatgit/workflows).

## How to use

1. Click **"Use this template"** on GitHub, pick a name for the new repo.
2. Clone the new repo locally.
3. Add the `CLAUDE_CODE_OAUTH_TOKEN` secret in the new repo's settings
   (Settings → Secrets and variables → Actions → New repository secret).
4. Open the project in your IDE and start with the **Concept Phase**
   (`/concept`) or jump straight into requirements if the concept is
   already settled.
5. Write a real `CLAUDE.md` at the root with project-specific commands,
   code layout, and gotchas. Delete this `README.md` or replace it.

## What's inside

```
.claude/settings.json            Claude Code permissions + model default
.github/workflows/               Stubs delegating to mthoatgit/workflows@v1
.gitignore                       Generic ignores + comment block for stack-specific entries
docs/
  specs/                         Phase 1 — Requirements (Epics + per-Epic specs)
    README.md                    Index template
    epics/E<N>-<slug>.md         Epic spec template
  architecture/
    system-design.md             Phase 2 — System design template
  tasks/
    backlog.md                   Phase 3 — Task index template
    epics/E<N>/T<NN>-<slug>.md   Task template
  tests/
    README.md                    Phase 4 — Test plan index template
    strategy.md                  Test strategy template
    cross-cutting.md             Cross-cutting tests template
    e2e.md                       End-to-end tests template
    epics/E<N>-<slug>.md         Per-Epic test scenarios template
```

## Workflow phases

The templates under `docs/` correspond to the phased workflow defined
in the `workflow-*` skills (`workflow-concept`, `workflow-requirements`,
`workflow-architecture`, `workflow-tasks`, `workflow-tests`,
`workflow-implementation`). The skills generate and update these files —
the templates here exist as a visible reference for the expected shape.

## Replacing the placeholders

Every template file contains `<PLACEHOLDER>` markers and a header block
naming the placeholders used in that file. Fill them in (or have a skill
do it) at the start of the corresponding phase.

## Related repositories

- [mthoatgit/workflows](https://github.com/mthoatgit/workflows) —
  reusable GitHub Actions workflows (pinned via `@v1` in the stubs here).
