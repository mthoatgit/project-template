# Workflow Backlog

Living list of process and tooling improvements to circle back on.
**Meta-level** — about the workflow itself (skills, orchestrator,
conventions), not about any single project's product features or bugs.

**Daten:** die Item-Tabelle steht in [`index.md`](index.md) — sie ist bewusst
prosa-frei gehalten, damit ein Frontend sie als reine Datenquelle parsen kann.
Diese README erklärt Zweck und Konventionen.

> **Current focus (Stand 2026-07-10, für nächste Session):** Wiedereinstieg bei Item [021 · Memory-Persistence — Migration ins Repo + Backup-Strategie](topics/021-memory-persistence-strategy.md). Die Diskussion wurde in dieser Session begonnen und bewusst vertagt; das Item enthält am Ende einen `Session-Kontext`-Block mit allen bereits geklärten Punkten und den nächsten konkreten Schritten. **Wenn du dieses Item startest, entferne diese Callout-Zeile** — sie ist Session-Handoff, nicht Dauer-Zustand.

## Struktur & Konventionen

Etabliert am 2026-07-10 (Item 001). Änderungen an der Struktur laufen wieder über ein Backlog-Item.

- **Scope.** Meta-Themen zum Workflow (Skills, Orchestrator, Konventionen). NICHT für Projekt-Features / -Bugs — die haben andere Homes (`docs/specs/`, `docs/tasks/`).
- **Ships only here.** Der Backlog-Ordner gehört zum project-template und beschreibt Design-Entscheidungen zum Prozess. Neue Projekte übernehmen ihn NICHT — sie brauchen ihn nicht.
- **Ein File pro Item.** Format `topics/<NNN>-<slug>.md` für aktive Items, `topics/archive/<NNN>-<slug>.md` für done/discarded. IDs stabil ab Vergabe (kein Renumbering bei Prio-Wechsel oder Löschung). Slug in kebab-case und trägt das Topic-Keyword für Grep.
- **Vier-Zeilen-Vertrag.** Jedes Item: **Symptom / Impact / Proposed shape / Source**. Bei P3 dürfen einzelne Bullets kurz sein, Struktur bleibt. Template unter `_TEMPLATE_ITEM.md`.
- **Timestamps.** Jede Zeile trägt `Created` und `Updated` (`YYYY-MM-DD HH:MM`). Beim Anlegen: beide gleich. Beim inhaltlichen Edit (inkl. Status-Flip mit Landed/Discarded-Sektion): `Updated` bumpen im selben Commit. Reine Struktur-Moves berühren `Updated` NICHT.
- **Archive.** Items mit Status `done` oder `discarded` liegen unter `topics/archive/`. Move erfolgt beim Status-Flip im selben Commit wie das Index-Update. `topics/` (Root) zeigt so nur aktive Themen.
- **Cross-References.** Backlog = Source of Truth. Memory (`project_orchestrator_open_issues.md`) verweist nur, dupliziert keinen Content. `docs/tasks/index.md` ist für akzeptierte Arbeit mit T/B-File — Graduation-Trigger: wir einigen uns "das bauen wir jetzt" → T/B-File anlegen → Backlog-Item wandert nach Archive mit Verweis auf die T/B-ID.
- **Adding.** Immer collaborativ. Wenn ich im Flow eine Lücke sehe, schlage ich vor (Titel + Prio-Vorschlag mit Begründung). Nie silent add. Adding = File-Op **UND** Zeileneintrag in `index.md` im **selben Commit**.
- **Consultation.** On-demand. User fragt "was steht offen" oder zeigt auf ein Item. Kein automatisches Session-Start-Skim.
- **Lifecycle-Exits.**
  - `done` — Item ist gelandet (Code committed **oder** Konvention in Skill / CLAUDE.md verankert). File nach `topics/archive/`, Status flippt in `index.md`, `Updated` bumpen. Ich frage aktiv nach wenn ein Item complete wirkt.
  - `discarded` — Item wurde überlegt und verworfen (misdiagnosed, YAGNI, überholt). Einzeiler-warum im Item-File anhängen, File nach `topics/archive/`, Status flippt, `Updated` bumpen.
- **Slash-Commands.** Bewusst keine. Manuelles Editieren + Konvention reichen bei aktueller Größe. Bei häufiger Index-Drift oder ID-Fehlgriffen später `/backlog-add` bauen — jetzt YAGNI.

## Prioritisation

- **P1** — Do next. Something is currently slipping or broken. Fixing prevents ongoing loss.
- **P2** — Design known, build when convenient. Not urgent.
- **P3** — Nice to have. Low value or exploratory.

## Sortierung in `index.md`

Nach Status gruppiert (open → done → discarded), innerhalb Gruppe nach ID aufsteigend.
