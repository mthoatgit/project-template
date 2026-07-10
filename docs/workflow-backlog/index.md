# Workflow Backlog

Living list of process and tooling improvements to circle back on.
**Meta-level** — about the workflow itself (skills, orchestrator,
conventions), not about any single project's product features or bugs.

## Struktur & Konventionen

Etabliert am 2026-07-10 (Item 001). Änderungen an der Struktur laufen wieder über ein Backlog-Item.

- **Scope.** Meta-Themen zum Workflow (Skills, Orchestrator, Konventionen). NICHT für Projekt-Features / -Bugs — die haben andere Homes (`docs/specs/`, `docs/tasks/`).
- **Ships only here.** Der Backlog-Ordner gehört zum project-template und beschreibt Design-Entscheidungen zum Prozess. Neue Projekte übernehmen ihn NICHT — sie brauchen ihn nicht.
- **Ein File pro Item.** Format `topics/<NNN>-<slug>.md` für aktive Items, `topics/archive/<NNN>-<slug>.md` für done/discarded. IDs stabil ab Vergabe (kein Renumbering bei Prio-Wechsel oder Löschung). Slug in kebab-case und trägt das Topic-Keyword für Grep.
- **Vier-Zeilen-Vertrag.** Jedes Item: **Symptom / Impact / Proposed shape / Source**. Bei P3 dürfen einzelne Bullets kurz sein, Struktur bleibt. Template unter `_TEMPLATE_ITEM.md`.
- **Timestamps.** Jede Zeile trägt `Created` und `Updated` (`YYYY-MM-DD HH:MM`). Beim Anlegen: beide gleich. Beim inhaltlichen Edit (inkl. Status-Flip mit Landed/Discarded-Sektion): `Updated` bumpen im selben Commit. Reine Struktur-Moves berühren `Updated` NICHT.
- **Archive.** Items mit Status `done` oder `discarded` liegen unter `topics/archive/`. Move erfolgt beim Status-Flip im selben Commit wie das Index-Update. `topics/` (Root) zeigt so nur aktive Themen.
- **Cross-References.** Backlog = Source of Truth. Memory (`project_orchestrator_open_issues.md`) verweist nur, dupliziert keinen Content. `docs/tasks/index.md` ist für akzeptierte Arbeit mit T/B-File — Graduation-Trigger: wir einigen uns "das bauen wir jetzt" → T/B-File anlegen → Backlog-Item wandert nach Archive mit Verweis auf die T/B-ID.
- **Adding.** Immer collaborativ. Wenn ich im Flow eine Lücke sehe, schlage ich vor (Titel + Prio-Vorschlag mit Begründung). Nie silent add. Adding = File-Op **UND** Zeileneintrag in dieser Index-Tabelle im **selben Commit**.
- **Consultation.** On-demand. User fragt "was steht offen" oder zeigt auf ein Item. Kein automatisches Session-Start-Skim.
- **Lifecycle-Exits.**
  - `done` — Item ist gelandet (Code committed **oder** Konvention in Skill / CLAUDE.md verankert). File nach `topics/archive/`, Status flippt im Index, `Updated` bumpen. Ich frage aktiv nach wenn ein Item complete wirkt.
  - `discarded` — Item wurde überlegt und verworfen (misdiagnosed, YAGNI, überholt). Einzeiler-warum im Item-File anhängen, File nach `topics/archive/`, Status flippt, `Updated` bumpen.
- **Slash-Commands.** Bewusst keine. Manuelles Editieren + Konvention reichen bei aktueller Größe. Bei häufiger Index-Drift oder ID-Fehlgriffen später `/backlog-add` bauen — jetzt YAGNI.

## Prioritisation

- **P1** — Do next. Something is currently slipping or broken. Fixing prevents ongoing loss.
- **P2** — Design known, build when convenient. Not urgent.
- **P3** — Nice to have. Low value or exploratory.

## Topics

Sortiert nach Status (open → done → discarded), innerhalb Gruppe nach ID aufsteigend.

| ID  | Prio | Titel                                                         | Status | Created          | Updated          | File                                                     |
|-----|------|---------------------------------------------------------------|--------|------------------|------------------|----------------------------------------------------------|
| 002 | P1   | Root Cause + Fix bleiben nach Bugfix leer                     | open   | 2026-07-09 21:31 | 2026-07-09 21:31 | [→](topics/002-root-cause-fix-empty.md)                  |
| 003 | P1   | Regression-Szenarien werden nicht in Epic-Test-Docs angehängt | open   | 2026-07-09 21:31 | 2026-07-09 21:31 | [→](topics/003-regression-scenarios-not-appended.md)     |
| 004 | P1   | `workflow-implementation` Skill kennt keine Bugs              | open   | 2026-07-09 21:31 | 2026-07-09 21:31 | [→](topics/004-workflow-implementation-task-only.md)     |
| 005 | P1   | Manuelle `fix:`-Commits umgehen Orchestrator-Bug-Flow         | open   | 2026-07-09 21:36 | 2026-07-09 21:36 | [→](topics/005-manual-fix-bypasses-orchestrator.md)      |
| 006 | P2   | Task-Implementation ohne expliziten Planning-Step             | open   | 2026-07-09 21:39 | 2026-07-09 21:39 | [→](topics/006-task-planning-step.md)                    |
| 007 | P2   | Test-Infra-Bugs vs. Code-Bugs unterscheiden                   | open   | 2026-07-09 21:31 | 2026-07-09 21:31 | [→](topics/007-test-infra-vs-code-bugs.md)               |
| 008 | P2   | `MAX_CONSECUTIVE_ABORTS` Cascade Guard                        | open   | 2026-07-09 21:31 | 2026-07-09 21:31 | [→](topics/008-max-consecutive-aborts-guard.md)          |
| 009 | P2   | Dirty Working Tree nach Abort                                 | open   | 2026-07-09 21:31 | 2026-07-09 21:31 | [→](topics/009-dirty-tree-after-abort.md)                |
| 010 | P2   | Structured-Smoke-Konzept                                      | open   | 2026-07-09 21:31 | 2026-07-09 21:31 | [→](topics/010-structured-smoke.md)                      |
| 011 | P2   | Logging prosa-vermischt, retrospektiv schwer auswertbar       | open   | 2026-07-09 21:38 | 2026-07-09 21:38 | [→](topics/011-logging-prose-mixed.md)                   |
| 012 | P2   | `/ship-epic` PR-Ceremony togglable per Projekt                | open   | 2026-07-09 21:55 | 2026-07-09 21:55 | [→](topics/012-ship-epic-togglable.md)                   |
| 013 | P2   | `docs/tasks/` Layout nicht final                              | open   | 2026-07-09 21:34 | 2026-07-09 21:34 | [→](topics/013-docs-tasks-layout.md)                     |
| 014 | P3   | Dashboard zeigt Type-Spalte nicht                             | open   | 2026-07-09 21:31 | 2026-07-09 21:31 | [→](topics/014-dashboard-type-column.md)                 |
| 015 | P3   | `MultiEdit`-Deny cosmetic Warning                             | open   | 2026-07-09 21:31 | 2026-07-09 21:31 | [→](topics/015-multiedit-deny-warning.md)                |
| 016 | P3   | feat/fix-Unterscheidung in Orchestrator-Commits               | open   | 2026-07-09 21:31 | 2026-07-09 21:31 | [→](topics/016-feat-fix-orchestrator-commits.md)         |
| 001 | P1   | Backlog-Struktur-Pass (Ordner + Index + Konventionen)         | done   | 2026-07-09 21:43 | 2026-07-10 08:49 | [→](topics/archive/001-backlog-structure-pass.md)        |
| 017 | —    | Entry-point-anchor test rule (`workflow-tests`)               | done   | 2026-07-09 21:31 | 2026-07-09 21:31 | [→](topics/archive/017-entry-point-anchor-test-rule.md)  |
| 018 | —    | Bug-flow Orchestrator variant                                 | done   | 2026-07-09 21:31 | 2026-07-09 21:31 | [→](topics/archive/018-bug-flow-orchestrator-variant.md) |
| 019 | —    | Merged work-item index (`docs/tasks/`)                        | done   | 2026-07-09 21:31 | 2026-07-09 21:31 | [→](topics/archive/019-merged-work-item-index.md)        |
| 020 | —    | `workflow-bugs` Skill                                         | done   | 2026-07-09 21:31 | 2026-07-09 21:31 | [→](topics/archive/020-workflow-bugs-skill.md)           |
