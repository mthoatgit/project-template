# project-template

Starter scaffolding for new projects. Combines the backlog-driven AI
workflow conventions, Claude Code settings, and the GitHub Actions
stubs that delegate to [mthoatgit/workflows](https://github.com/mthoatgit/workflows).

## Getting Started

### One-time setup (per new repo)

1. Click **"Use this template"** on GitHub → pick a name, clone locally.
2. Add the OAuth secret: **Settings → Secrets and variables → Actions →**
   `CLAUDE_CODE_OAUTH_TOKEN`.
3. Open the project in your IDE with Claude Code installed.
4. Run **`/init-project`** — fills the root `CLAUDE.md`, replaces this
   `README.md` with a real project README, resets `docs/backlog/`, and
   files **item 001** with your seed idea. You can also do these steps
   manually if you prefer.

Alternatively, from an existing Claude Code session in another project,
run **`/new-project <name>`** — it clones this template, wipes history,
and applies `/init-project` to the new directory in one flow.

### The workflow in one paragraph

Everything starts as a **backlog item** in `docs/backlog/`. Each item's
type binds it to a **lifecycle** that defines the stages it runs through:

- **featurework** (5 stages) for `idea`, `gap`, `improvement` — Concept → Requirements → Architecture → Task-Breakdown → Tests
- **bug** (4 stages) for `bug` — Reproduction → Root cause → Regression test → Fix
- **question** (2 stages) for `question` — Investigation → Answer

Each stage is deliberately entered, has its own approval gate, and
produces its own commit — **never bundled** with adjacent stages. The
design conversation for a stage happens inside that stage's
`### Discussion` sub-section in the item file itself; artefacts
(`concept.md`, REQs, ADRs, task files, test scenarios, B-files) live in
their respective `docs/` folders and back-link to the item as their
`Source`. When all applicable stages complete, the item flips to `done`
and moves to `docs/backlog/archive/` in the same commit as the final
stage's output.

Item 001 is a naming convention: `/init-project` files it as the
project's origin story, its Stage 1 writes the initial `docs/concept.md`,
and its Stage 3 always produces `ADR-0001` (tech stack) per the
**founding-ADR rule** — the project-wide architectural commitment.

For the full flow diagram + skill map, see [`docs/workflow-overview.md`](docs/workflow-overview.md).

### Typical first session

```text
/init-project "<name>"            ← Bootstrap — CLAUDE.md + README + docs/backlog/001-<seed-slug>.md
/backlog 001                      ← Enter Stage 1 (Concept) — design conversation in the item body
... approve Stage 1, commit ...   ← docs/concept.md written, item Outcome back-links to commit
                                    Stage 2 (REQ + Epic-Birth) writes docs/specs/epics/E1-<slug>/REQ-<NNNN>-*.md
... approve Stage 2, commit ...
                                    Stage 3 (Architecture) writes ADR-0001 (founding tech stack)
... approve Stage 3, commit ...
                                    Stage 4 (Task-Breakdown) writes docs/tasks/TASK-<NNNN>-*.md (flat, no E<N>/ subdir)
... approve Stage 4, commit ...
                                    Stage 5 (Tests) writes docs/tests/TEST-<NNNN>-*.md files (one per verification atom, three-mode) — item archives
... approve Stage 5, commit ...
/start-epic 1                     ← Implementation phase — orchestrator-driven TDD loop
/ship-epic                        ← Self-review + open PR
```

Subsequent items follow the same pattern:

- **`/backlog <oneliner>`** — file a new item (type is asked or inferred)
- **`/backlog <NNN-slug>`** — resume an existing item at its current stage
- **`/backlog`** — browse open items grouped by type

Cross-item references via `## Related` links carry the graph. When a
bug's Root Cause reveals a spec gap, a follow-up `idea` / `improvement`
item is filed and the two back-link.

## What's inside

```
CLAUDE.md                        Project-specific context template (filled by /init-project)
README.md                        This file (replaced by /init-project)
.claude/settings.json            Claude Code permissions + model default
.github/workflows/               Stubs delegating to mthoatgit/workflows@v1
.gitignore                       Generic ignores + comment block for stack-specific entries
orchestrator/                    Implementation-phase TDD driver (Ralph Loop + DoD gates)
docs/
  workflow-overview.md           Lifecycle diagrams + skill map + Golden Rules
  concept.md                     Living project overview (Stage 1 of item 001, amended by later items)
  backlog/                       Universal capture — bugs, ideas, gaps, questions, improvements
    README.md                    Backlog conventions + priority scheme
    index.md                     Prose-free item table (data source)
    _TEMPLATE_bug.md             Type-specific day-zero templates
    _TEMPLATE_idea.md
    _TEMPLATE_gap.md
    _TEMPLATE_question.md
    _TEMPLATE_improvement.md
    archive/                     Terminal items (done / dropped / superseded / wont-fix / cant-repro)
  specs/                         Requirements — Epic files
    README.md
    epics/_TEMPLATE.md           Epic spec blueprint (copied per Epic)
    cross-cutting/_TEMPLATE.md   Cross-cutting NFRs blueprint (copied per concern)
  architecture/
    system-design.md             Living system design (amended alongside its driving ADR)
  adr/                           Architecture decisions
    README.md
    _TEMPLATE.md
  tasks/                         Implementation work items (merged namespace: T<NN> tasks + B<NN> bug fixes)
    index.md                     Merged status table (Type column distinguishes task vs bug)
    README.md                    Flat-layout orientation
    _TEMPLATE_TASK.md            Task blueprint (feature tasks)
    _TEMPLATE_BUG.md             BUG-file blueprint (thin — the orchestrator's fix interface)
    TASK-<NNNN>-*.md             Task work items (flat per REQ-0006, no E<N>/ subdirectory)
    BUG-<NNNN>-*.md              Bug work items (flat, shared counter with TASK-)
  tests/                         Test specs — one file per verification atom, three-mode framework
    README.md
    strategy.md                  Three-mode framing (behavioral/structural/procedural) + pyramid + CI
    index.md                     All tests with ID / Epic / Mode / REQ / Task / Status columns
    _TEMPLATE_BEHAVIORAL.md      Behavioral (pytest / flutter test) test spec blueprint
    _TEMPLATE_STRUCTURAL.md      Structural (shell / grep) test spec blueprint
    _TEMPLATE_PROCEDURAL.md      Procedural (human-playbook) test spec blueprint
    TEST-<NNNN>-*.md             Individual test specs (flat, one per verification atom)
    cross-cutting/               Tests for NFRs / system-wide concerns without single-Epic owner
```

## Replacing the placeholders

Every template file contains `<PLACEHOLDER>` markers and a header block
naming the placeholders used in that file. Fill them in (or have a skill
do it) at the corresponding lifecycle stage.

### Template marker convention

Template files are signalled in two ways:

1. **YAML frontmatter** at the top of the file:
   ```yaml
   ---
   status: template
   ---
   ```
   Machine-readable — skills check this to know the file is still placeholder.
2. **Inline banner** below the title (`> **Template file.** ...`) —
   human-readable, explains how to fill the file in.

**When filling a file with real content, remove BOTH the frontmatter and
the banner.** A file without these markers is considered real content.

Two flavors of template files exist:

| Flavor | Examples | Lifecycle |
|---|---|---|
| **Multi-instance blueprints** (`_TEMPLATE_*.md`) | `docs/backlog/_TEMPLATE_idea.md`, `docs/specs/epics/_TEMPLATE.md`, `docs/specs/epics/_REQ-TEMPLATE.md`, `docs/tasks/_TEMPLATE_TASK.md`, `docs/tasks/_TEMPLATE_BUG.md`, `docs/tests/_TEMPLATE_BEHAVIORAL.md`, `docs/tests/_TEMPLATE_STRUCTURAL.md`, `docs/tests/_TEMPLATE_PROCEDURAL.md` | Stay as templates forever. Copied to produce real files (`E1-foo/E1-foo.md`, `REQ-0001-bar.md`, `TASK-0001-baz.md`, `TEST-0001-quux.md`, `001-my-slug.md`). The copy inherits the frontmatter; remove it when filling in. |
| **Single-instance placeholders** | `docs/concept.md`, `docs/architecture/system-design.md`, `docs/specs/README.md`, `docs/tests/README.md`, `docs/tests/strategy.md`, etc. | One file at the final path with placeholder content. Frontmatter is removed once the file holds real content. |

## Related repositories

- [mthoatgit/workflows](https://github.com/mthoatgit/workflows) —
  reusable GitHub Actions workflows (pinned via `@v1` in the stubs here).
