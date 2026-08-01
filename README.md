# project-template

Starter scaffolding for new projects. Combines the backlog-driven AI
workflow conventions, Claude Code settings, and the GitHub Actions
stubs that delegate to [mthoatgit/workflows](https://github.com/mthoatgit/workflows).

## Dual-nature layout

Everything a downstream project starts with lives under [`skeleton/`](skeleton/). Everything at the repo root outside `skeleton/` is project-template's own project (its `CLAUDE.md`, backlog, orchestrator tests, etc.) — those files do NOT propagate downstream.

```
project-template/
├── skeleton/              ← copied verbatim into every new project
│   ├── CLAUDE.md          (template)
│   ├── README.md          (template)
│   ├── .claude/, .github/, .gitignore, .gitattributes
│   ├── orchestrator/      ← the canonical orchestrator source
│   └── docs/              ← templates + shared workflow reference
│
├── CLAUDE.md              ← project-template's own maintainer context
├── README.md              ← this file
├── docs/                  ← project-template's OWN backlog + (future) REQs/tasks/tests/ADRs
├── orchestrator-tests/    ← pytest suite for the orchestrator
└── pytest.ini             ← testpaths + pythonpath config for `pytest`
```

`/new-project` copies `skeleton/*` into the target directory and runs `/init-project` fill logic (project name, seed item 001). project-template develops itself using the same phased workflow — items live in the ROOT `docs/backlog/` (not `skeleton/docs/backlog/`), REQs / tasks / tests / ADRs also file at root.

## Getting Started (downstream)

### One-time setup (per new repo)

1. Click **"Use this template"** on GitHub → pick a name, clone locally.
2. Add the OAuth secret: **Settings → Secrets and variables → Actions →** `CLAUDE_CODE_OAUTH_TOKEN`.
3. Open the project in your IDE with Claude Code installed.
4. Run **`/init-project`** — fills `CLAUDE.md`, replaces `README.md` with a real project README, seeds **item 001** with your seed idea.

Alternatively, from an existing Claude Code session in another project, run **`/new-project <name>`** — it copies `skeleton/*` and applies `/init-project` in one flow.

### The workflow in one paragraph

Everything starts as a **backlog item** in `docs/backlog/`. Each item's type binds it to a **lifecycle** that defines the stages it runs through:

- **featurework** (5 stages) for `idea`, `gap`, `improvement` — Concept → Requirements → Architecture → Task-Breakdown → Tests
- **bug** (4 stages) for `bug` — Reproduction → Root cause → Regression test → Fix
- **question** (2 stages) for `question` — Investigation → Answer

Each stage is deliberately entered, has its own approval gate, and produces its own commit — **never bundled** with adjacent stages. The design conversation for a stage happens inside that stage's `### Discussion` sub-section in the item file itself; artefacts (`concept.md`, REQs, ADRs, task files, test scenarios) live in their respective `docs/` folders and back-link to the item as their `Source`. When all applicable stages complete, the item flips to `done` and moves to `docs/backlog/archive/` in the same commit as the final stage's output.

Item 001 is a naming convention: `/init-project` files it as the project's origin story, its Stage 1 writes the initial `docs/concept.md`, and its Stage 3 always produces `ADR-0001` (tech stack) per the **founding-ADR rule**.

For the full flow diagram + skill map, see [`skeleton/docs/workflow-overview.md`](skeleton/docs/workflow-overview.md).

### Typical first session (downstream)

```text
/init-project "<name>"            ← Bootstrap — CLAUDE.md + README + docs/backlog/001-<seed-slug>.md
/backlog 001                      ← Enter Stage 1 (Concept) — design conversation in the item body
... approve Stage 1, commit ...   ← docs/concept.md written, item Outcome back-links to commit
                                    Stage 2 (REQ + Epic-Birth) writes docs/specs/epics/E1-<slug>/REQ-<NNNN>-*.md
... approve Stage 2, commit ...
                                    Stage 3 (Architecture) writes ADR-0001 (founding tech stack)
... approve Stage 3, commit ...
                                    Stage 4 (Task-Breakdown) writes docs/tasks/TASK-<NNNN>-*.md
... approve Stage 4, commit ...
                                    Stage 5 (Tests) writes docs/tests/TEST-<NNNN>-*.md (item archives)
... approve Stage 5, commit ...
/start-epic 1                     ← Implementation phase — orchestrator-driven TDD loop
/ship-epic                        ← Self-review + open PR
```

## What's inside

```
skeleton/                          Everything copied into new downstream projects
├── CLAUDE.md                       Project-specific context template (filled by /init-project)
├── README.md                       Downstream README template (replaced by /init-project)
├── .claude/settings.json           Claude Code permissions + model default
├── .github/workflows/              CI stubs delegating to mthoatgit/workflows@v1
├── .gitignore, .gitattributes      Generic ignores + line-ending normalization
├── orchestrator/                   Implementation-phase TDD driver (Ralph Loop + DoD gates)
└── docs/
    ├── workflow-overview.md        Lifecycle diagrams + skill map + Golden Rules
    ├── concept.md                  Living project overview (Stage 1 of item 001)
    ├── backlog/                    Universal capture — bugs, ideas, gaps, questions, improvements
    │   ├── README.md, index.md, _TEMPLATE_*.md, archive/
    ├── specs/                      Requirements — Epic files
    │   ├── README.md
    │   ├── epics/_TEMPLATE.md, _REQ-TEMPLATE.md
    │   └── cross-cutting/_TEMPLATE.md
    ├── architecture/system-design.md
    ├── adr/                        Architecture decisions (README + _TEMPLATE)
    ├── tasks/                      Implementation work items (TASK/BUG shared namespace)
    │   └── README.md, index.md, _TEMPLATE_TASK.md, _TEMPLATE_BUG.md
    └── tests/                      Test specs (three-mode framework)
        └── README.md, strategy.md, index.md, _TEMPLATE_{BEHAVIORAL,STRUCTURAL,PROCEDURAL}.md, cross-cutting/

CLAUDE.md                          project-template's own maintainer context
README.md                          this file
docs/                              project-template's own docs (backlog + future REQs/tasks/tests/ADRs)
orchestrator-tests/                pytest suite for the orchestrator (root-only, not in skeleton)
pytest.ini                         testpaths + pythonpath config for the orchestrator tests
```

## Replacing the placeholders (downstream)

Template files are signalled by (1) `status: template` YAML frontmatter and (2) an inline banner. When filling with real content, remove both.

- **Multi-instance blueprints** (`_TEMPLATE_*.md`) stay as templates forever; copied to produce real files (`REQ-0001-bar.md`, `TASK-0001-baz.md`, `TEST-0001-quux.md`, `001-my-slug.md`).
- **Single-instance placeholders** (`docs/concept.md`, `docs/architecture/system-design.md`, `docs/specs/README.md`, `docs/tests/README.md`, `docs/tests/strategy.md`, `CLAUDE.md`, `README.md`): one file at the final path with placeholder content; frontmatter removed when filled.

## Related repositories

- [mthoatgit/workflows](https://github.com/mthoatgit/workflows) — reusable GitHub Actions workflows (pinned via `@v1` in the stubs here).
- [mthoatgit/dotfiles-claude](https://github.com/mthoatgit/dotfiles-claude) — the `~/.claude/` skills + commands + rules that this template's workflow depends on.
