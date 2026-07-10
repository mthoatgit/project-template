# Workflow Backlog

Living list of process and tooling improvements to circle back on.
**Meta-level** — about the workflow itself (skills, orchestrator,
conventions), not about any single project's product features or bugs.

## Struktur & Konventionen

Etabliert am 2026-07-10 (Item 001). Änderungen an der Struktur laufen wieder über ein Backlog-Item.

- **Scope.** Meta-Themen zum Workflow (Skills, Orchestrator, Konventionen). NICHT für Projekt-Features / -Bugs — die haben andere Homes (`docs/specs/`, `docs/tasks/`).
- **Ships only here.** Der Backlog-Ordner gehört zum project-template und beschreibt Design-Entscheidungen zum Prozess. Neue Projekte übernehmen ihn NICHT — sie brauchen ihn nicht.
- **Ein File pro Item.** Format `<NNN>-<slug>.md` im selben Ordner. IDs stabil ab Vergabe (kein Renumbering bei Prio-Wechsel oder Löschung). Slug in kebab-case und trägt das Topic-Keyword für Grep.
- **Vier-Zeilen-Vertrag.** Jedes Item: **Symptom / Impact / Proposed shape / Source**. Bei P3 dürfen einzelne Bullets kurz sein, Struktur bleibt. Template unter `_TEMPLATE_ITEM.md`.
- **Cross-References.** Backlog = Source of Truth. Memory (`project_orchestrator_open_issues.md`) verweist nur, dupliziert keinen Content. `docs/tasks/index.md` ist für akzeptierte Arbeit mit T/B-File — Graduation-Trigger: wir einigen uns "das bauen wir jetzt" → T/B-File anlegen → Backlog-Item wandert nach Done mit Verweis auf die T/B-ID.
- **Adding.** Immer collaborativ. Wenn ich im Flow eine Lücke sehe, schlage ich vor (Titel + Prio-Vorschlag mit Begründung). Nie silent add. Adding = File-Op **UND** Zeileneintrag in dieser Index-Tabelle im **selben Commit**.
- **Consultation.** On-demand. User fragt "was steht offen" oder zeigt auf ein Item. Kein automatisches Session-Start-Skim.
- **Lifecycle-Exits.**
  - `done` — Item ist gelandet (Code committed **oder** Konvention in Skill / CLAUDE.md verankert). File bleibt in-place, Status flippt im Index. Ich frage aktiv nach wenn ein Item complete wirkt.
  - `discarded` — Item wurde überlegt und verworfen (misdiagnosed, YAGNI, überholt). Einzeiler-warum im Item-File anhängen, Status flippt.
- **Slash-Commands.** Bewusst keine. Manuelles Editieren + Konvention reichen bei aktueller Größe. Bei häufiger Index-Drift oder ID-Fehlgriffen später `/backlog-add` bauen — jetzt YAGNI.

## Prioritisation

- **P1** — Do next. Something is currently slipping or broken. Fixing prevents ongoing loss.
- **P2** — Design known, build when convenient. Not urgent.
- **P3** — Nice to have. Low value or exploratory.

## Open

| ID  | Prio | Titel                                                        | Status |
|-----|------|--------------------------------------------------------------|--------|
| [002](002-root-cause-fix-empty.md)                          | P1 | Root Cause + Fix bleiben nach Bugfix leer                     | open |
| [003](003-regression-scenarios-not-appended.md)             | P1 | Regression-Szenarien werden nicht in Epic-Test-Docs angehängt | open |
| [004](004-workflow-implementation-task-only.md)             | P1 | `workflow-implementation` Skill kennt keine Bugs              | open |
| [005](005-manual-fix-bypasses-orchestrator.md)              | P1 | Manuelle `fix:`-Commits umgehen Orchestrator-Bug-Flow         | open |
| [006](006-task-planning-step.md)                            | P2 | Task-Implementation ohne expliziten Planning-Step             | open |
| [007](007-test-infra-vs-code-bugs.md)                       | P2 | Test-Infra-Bugs vs. Code-Bugs unterscheiden                   | open |
| [008](008-max-consecutive-aborts-guard.md)                  | P2 | `MAX_CONSECUTIVE_ABORTS` Cascade Guard                        | open |
| [009](009-dirty-tree-after-abort.md)                        | P2 | Dirty Working Tree nach Abort                                 | open |
| [010](010-structured-smoke.md)                              | P2 | Structured-Smoke-Konzept                                      | open |
| [011](011-logging-prose-mixed.md)                           | P2 | Logging prosa-vermischt, retrospektiv schwer auswertbar       | open |
| [012](012-ship-epic-togglable.md)                           | P2 | `/ship-epic` PR-Ceremony togglable per Projekt                | open |
| [013](013-docs-tasks-layout.md)                             | P2 | `docs/tasks/` Layout nicht final                              | open |
| [014](014-dashboard-type-column.md)                         | P3 | Dashboard zeigt Type-Spalte nicht                             | open |
| [015](015-multiedit-deny-warning.md)                        | P3 | `MultiEdit`-Deny cosmetic Warning                             | open |
| [016](016-feat-fix-orchestrator-commits.md)                 | P3 | feat/fix-Unterscheidung in Orchestrator-Commits               | open |

## Landed / Discarded

Chronologisch nach Landung — jüngste zuerst. Einträge bleiben permanent (kein Archiv).

| ID  | Prio | Titel                                                        | Status |
|-----|------|--------------------------------------------------------------|--------|
| [001](001-backlog-structure-pass.md)                        | P1 | Backlog-Struktur-Pass (Ordner + Index + Konventionen)         | done |
| [020](020-workflow-bugs-skill.md)                           | —  | `workflow-bugs` Skill                                         | done |
| [019](019-merged-work-item-index.md)                        | —  | Merged work-item index (`docs/tasks/`)                        | done |
| [018](018-bug-flow-orchestrator-variant.md)                 | —  | Bug-flow Orchestrator variant                                 | done |
| [017](017-entry-point-anchor-test-rule.md)                  | —  | Entry-point-anchor test rule (`workflow-tests`)               | done |
