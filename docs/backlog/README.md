# Backlog

Living list of items to circle back on — bugs, ideas, gaps, questions, improvements. Universal capture-and-shape flow per the `workflow-backlog` skill.

**Scope of THIS backlog (project-template):** meta-level items about the workflow itself — skills, orchestrator, conventions. Every downstream project scaffolded from this template gets its own separate `docs/backlog/` for its own product-level items; they never share.

**Daten:** die Item-Tabelle steht in [`index.md`](index.md) — sie ist bewusst prosa-frei gehalten, damit ein Frontend sie als reine Datenquelle parsen kann. Diese README erklärt Zweck und Konventionen.

## Struktur & Konventionen

Etabliert am 2026-07-10 (Item 001), universal refactored am 2026-07-19 mit Type-Feld + `/backlog`-Command. Änderungen an der Struktur laufen wieder über ein Backlog-Item.

- **Types.** Fünf: `bug`, `idea`, `gap`, `question`, `improvement`. Jeder Type hat eigenes Template (`_TEMPLATE_<type>.md`) mit typ-spezifischen Capture-Fragen. Migrated items aus der pre-refactor Ära tragen `type: improvement` — historische Approximation, kein Umschreiben.
- **Ein File pro Item.** Format `<NNN>-<slug>.md` für aktive Items, `archive/<NNN>-<slug>.md` für done/dropped/superseded. IDs stabil ab Vergabe (globaler Zähler über alle Types, kein Renumbering). Slug in kebab-case und trägt das Topic-Keyword für Grep.
- **Universal frontmatter.** Neue Items tragen `type`, `status`, `priority`, `created`, `updated` als YAML-Frontmatter. Migrierte Items tragen minimal nur `type` — historische Ausnahme.
- **Timestamps.** Jede Zeile im Index trägt `Created` und `Updated` (`YYYY-MM-DD HH:MM`). Beim Anlegen: beide gleich. Beim inhaltlichen Edit (inkl. Status-Flip): `updated` im Frontmatter UND `Updated`-Cell im Index bumpen im selben Commit. Reine Struktur-Moves berühren `Updated` NICHT.
- **Archive-on-terminal.** Items mit Status `done`, `dropped`, oder `superseded` liegen unter `archive/`. Move erfolgt im selben Commit wie das Status-Flip und das Index-Update. `docs/backlog/` (Root) zeigt so nur aktive Themen.
- **Cross-References.** Backlog ist SoT für offene Diskussionen und die Lebens-Ledger der Items. `docs/tasks/index.md` ist für akzeptierte Arbeit mit T/B-File. Graduation-Trigger: das Item durchläuft seinen Lifecycle (z.B. featurework Stage 4 produziert die T-Files), die Stage-Outcomes im Item verlinken alle produzierten Artefakte. Beim finalen Stage flippt der Item-Status auf `done` und wandert nach `archive/`.
- **Adding.** Immer collaborativ. Nie silent add. Adding = File-Op **UND** Zeileneintrag in `index.md` im **selben Commit**. `/backlog <type> <oneliner>` automatisiert das.
- **Consultation.** On-demand. User fragt „was steht offen" oder zeigt auf ein Item. Kein automatisches Session-Start-Skim.
- **Slash-Command.** `/backlog` — universeller Entry-Point. Modi:
  - `/backlog` — browse alle offenen Items nach Type gruppiert
  - `/backlog <type> <oneliner>` — neues Item, Type direkt gegeben
  - `/backlog <oneliner>` — neues Item, Type wird interaktiv gefragt
  - `/backlog <NNN-slug>` — existierendes Item öffnen / erweitern / promoten
- **Lifecycle & Stages.** Jeder Item-Type ist an einen Lifecycle gebunden, der die Stages definiert die er durchläuft. `workflow-lifecycle-featurework` für idea/gap/improvement (5 Stages), `workflow-lifecycle-bug` für bug (4 Stages), `workflow-lifecycle-question` für question (2 Stages). Item's `**Lifecycle:**` Header-Zeile zeigt drauf. Stage-Sections wachsen im Item-Body je nachdem in welcher Stage gerade gearbeitet wird.
- **Terminal-Exits.**
  - `done` — Alle applicable Stages abgeschlossen. File nach `archive/`, Status flippt im Index, `updated` bumpen.
  - `dropped` — Item wurde überlegt und verworfen (misdiagnosed, YAGNI, überholt). Einzeiler-warum in der aktuellen Stage's Discussion, File nach `archive/`.
  - `superseded` — Item durch anderes ersetzt. `## Related` bekommt `Superseded <YYYY-MM-DD> by [[NNN-slug]]. Reason: <one line>.` File nach `archive/`.
  - `wont-fix` — bug-only. Bug entschieden nicht zu fixen. Reason im Bug-File. File nach `archive/`.
  - `cant-repro` — bug-only. Stage 1 (Reproduction) endete ohne Reproducer. File nach `archive/`.

## Prioritisation

Backlog-triage priority — a "when to work on this item" signal for the item itself. Not to be confused with priority concepts elsewhere in the project (e.g. spec-level acceptance urgency, ADR-level severity, or external tracker priorities). When reading `priority` in item frontmatter, the scope is always "should we pull this from the backlog next?".

- **P1** — Do next. Something is currently slipping or broken. Fixing prevents ongoing loss.
- **P2** — Design known, build when convenient. Not urgent.
- **P3** — Nice to have. Low value or exploratory.

## Sortierung in `index.md`

Nach Status gruppiert (open → done → dropped → superseded → wont-fix → cant-repro), innerhalb Gruppe nach ID aufsteigend.
