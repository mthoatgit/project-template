# Workflow Overview

A visual map of the phased, spec-driven workflow this template implements.
The phase rules themselves live in `~/.claude/skills/workflow-*/SKILL.md`
(global, apply to every project cloned from this template) — this file is
a quick-recall reference, not a source of truth. If it drifts from the
skills, the skills win.

## Main Flow

```mermaid
flowchart TD
    Idea(["New idea"]) --> Concept
    Concept["Phase 0 — Concept<br/>ripen 001 in /backlog<br/>→ snapshot to docs/concept.md"]
    Concept -->|approve| Requirements
    Requirements["Phase 1 — Requirements<br/>→ docs/specs/README.md<br/>→ docs/specs/epics/E&lt;N&gt;-*.md"]
    Requirements -->|approve| RiskCheck{"Technical risk?"}
    RiskCheck -->|yes| Spike["Phase 1.5 — Spike<br/>/spike<br/>branch spike/&lt;slug&gt; — never merged<br/>→ docs/adr/&lt;NNNN&gt;-*.md"]
    RiskCheck -->|no| Architecture
    Spike --> Architecture
    Architecture["Phase 2 — Architecture<br/>→ docs/architecture/system-design.md<br/>→ docs/adr/0001-tech-stack.md"]
    Architecture -->|approve| Tasks
    Tasks["Phase 3 — Tasks<br/>→ docs/tasks/E&lt;N&gt;/T&lt;NN&gt;-*.md<br/>→ docs/tasks/index.md"]
    Tasks -->|approve| Tests
    Tests["Phase 4 — Tests<br/>→ docs/tests/README.md<br/>→ docs/tests/strategy.md<br/>→ docs/tests/epics/E&lt;N&gt;-*.md"]
    Tests -->|approve| Implementation
    Implementation["Phase 5-7 — Implementation<br/>see sub-flow below"]
    Implementation --> Merged(["PR merged"])
    Merged -.->|next Epic| Requirements

    classDef gate fill:#fff3cd,stroke:#d4a017,color:#333;
    classDef doc fill:#eef2ff,stroke:#6366f1,color:#333;
    classDef terminal fill:#dcfce7,stroke:#16a34a,color:#333;
    class RiskCheck gate;
    class Concept,Requirements,Spike,Architecture,Tasks,Tests,Implementation doc;
    class Idea,Merged terminal;
```

Every arrow labeled `approve` is a hard stop: the phase ends with an
explicit approval request, and nothing in the next phase starts before
the user confirms. The Spike is the only optional phase — most Epics skip
it and go straight from Requirements to Architecture.

## Implementation Sub-Flow (per Epic)

```mermaid
flowchart TD
    S1["/start-epic &lt;N&gt;<br/>reads Epic file + tasks<br/>outputs confirmation block"] -->|user confirms go| S2["create branch<br/>epic/&lt;n&gt;-&lt;slug&gt; from main"]
    S2 --> S3["/scaffold &lt;N&gt;<br/>empty skeletons only, no logic<br/>commit: [scaffold] E&lt;N&gt;"]
    S3 --> S4["python -m orchestrator starts"]
    S4 --> Loop{"next task<br/>T&lt;NN&gt;?"}
    Loop -->|yes| Ralph["Ralph Loop<br/>Claude implements + writes tests"]
    Ralph --> RunTests["run test-cmd"]
    RunTests -->|fail| Ralph
    RunTests -->|pass| Critic["Critic-Actor<br/>adversarial design review"]
    Critic -->|rejected| Ralph
    Critic -->|approved| Commit["commit: feat: &lt;title&gt; (T&lt;NN&gt;)"]
    Commit --> Loop
    Loop -->|no — all done| Ship["/ship-epic"]
    Ship --> Review["verify commit history<br/>self-review acceptance criteria"]
    Review --> Reflect["Reflect: scan upstream docs<br/>for drift caused by what was built"]
    Reflect -->|user approves fixes| DriftCommit["docs: commit<br/>(drift corrections)"]
    DriftCommit --> Push["git push"]
    Push --> PRCreate["gh pr create"]
    PRCreate --> Human(["user reviews and merges"])

    classDef gate fill:#fff3cd,stroke:#d4a017,color:#333;
    classDef terminal fill:#dcfce7,stroke:#16a34a,color:#333;
    class Loop gate;
    class Human terminal;
```

Claude never runs `git checkout -b`, never commits during the loops
(the orchestrator owns the per-task commit), and never merges or pushes
to `main` directly — the user always merges.

## Phase Reference

| Phase | Skill | Command(s) | Primary output |
|---|---|---|---|
| 0 — Concept | `workflow-backlog` (ripening) + `workflow-concept` (artifact) | `/backlog 001` → snapshot promotion | `docs/concept.md` |
| 1 — Requirements | `workflow-requirements` | always via `/backlog` promotion (1..N REQs per item) — at Phase 1 kick-off just in rapid succession | `docs/specs/README.md`, `docs/specs/epics/E<N>-*.md` |
| 1.5 — Spike (optional) | `workflow-spike` | `/spike <question>` | `docs/adr/<NNNN>-*.md`, branch `spike/<slug>` |
| 2 — Architecture | `workflow-architecture` | — | `docs/architecture/system-design.md`, `docs/adr/0001-tech-stack.md` |
| 3 — Tasks | `workflow-tasks` | — | `docs/tasks/E<N>/T<NN>-*.md`, `docs/tasks/index.md` |
| 4 — Tests | `workflow-tests` | — | `docs/tests/README.md`, `docs/tests/strategy.md`, `docs/tests/epics/E<N>-*.md` |
| 5-7 — Implementation | `workflow-implementation` | `/start-epic`, `/scaffold`, `python -m orchestrator`, `/ship-epic` | code + tests, one PR per Epic |
| cross-cutting | `workflow-epics` | — | Epic naming/sizing conventions used by every phase above |
| reactive (post-done) | `workflow-bugs` | — | `docs/tasks/E<N>/B<NN>-*.md`, entries in `docs/tasks/index.md` (Type: bug) |

Skills live at `~/.claude/skills/workflow-*/SKILL.md` and are global —
they apply to every project cloned from this template, not just this repo.

## Easy-to-Forget Concepts

- **Three levels of acceptance criteria, not one:**
  `REQ-AC` (Phase 1, behavioral) → `Epic-AC` (Phase 3, user-observable) →
  `Task-AC` (Phase 3, technical). Later levels refine earlier ones; they
  must never contradict them.
- **Requirements are append-only.** A substantial change to an approved
  requirement is a *supersession* (`STATUS: superseded by <new-ID>`), not
  an edit in place. IDs are never reused or renumbered.
- **Epic sizing:** 3–8 tasks, demoable in 30 seconds after merge. Smaller
  is noise, larger is unreviewable. A pure refactor with no user-visible
  delta is not an Epic.
- **Template-file marker:** files awaiting real content carry
  `status: template` frontmatter + an inline banner. Remove both when
  filling them for real — a file without these markers is real content,
  never edit it as if it were still a placeholder.
- **Foundational contradictions mid-Epic** (architecture can't work,
  a requirement turns out impossible) stop everything immediately and
  propagate upstream with user go-ahead — this is different from the
  routine drift the Reflect step handles at `/ship-epic` time.

## Golden Rules

**Never:**
- Skip phases
- Implement without an approved task or bug
- Change architecture without approval
- Add unrelated features
- Modify unrelated files

**Always:**
- Stay within task scope
- Ask when uncertain
- Prefer simplicity over complexity
- Follow acceptance criteria strictly
