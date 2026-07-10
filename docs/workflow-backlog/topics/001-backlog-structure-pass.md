# P1 · Backlog itself needs a structure pass before it grows

- **Symptom.** This backlog was seeded 2026-07-09 with 14 open items in a flat single-file list. No convention yet for how items are added, prioritised, moved to Done, archived, or cross-referenced with the memory system and `docs/tasks/index.md`. Currently ad-hoc.
- **Impact.** If items pile up in a poor structure, reorganising later will be expensive and context gets lost. The backlog is the tool that manages every other open item — getting it wrong compounds. Better to shape it while the file is still small.
- **Proposed shape.** Open. Discussion needed across four question groups — captured here so a cold-read tomorrow picks up where we left off:
  - **Lifecycle.** When do we consult it (session start / planning cycle / on demand)? Who adds items (Claude on user request, or spontaneously)? Who prioritises P1/P2/P3 — my "what's slipping" bias may not match yours. What happens to items that turn out wrong or obsolete: delete, mark superseded, move to a "Discarded" section?
  - **Growth.** Stay as one file, or split by category (orchestrator / skills / tooling / conventions)? At 40+ items how do we keep them findable — plain grep, tags, an index at the top? Does the Done section grow unbounded, or archive after X months / N items? Is the four-line contract per item (Symptom / Impact / Proposed shape / Source) worth the overhead at scale, or should it collapse for low-priority items?
  - **Cross-references.** Backlog vs. memory (`project_orchestrator_open_issues.md`) currently overlaps heavily — what's each one's role, or should they merge? Backlog vs. `docs/tasks/index.md` — when does an item graduate from "concept in backlog" to "task in index"? Does the backlog belong in the project-template (ships to every new project) or does each project need its own project-specific backlog too?
  - **Ritual.** Do we need a triage cadence ("walk the backlog on session start" or "weekly")? How do I make sure Claude in a fresh session actually consults the backlog — memory pointer? Explicit slash command `/backlog`? Do we want commands (`/backlog add`, `/backlog move`, `/backlog done`) or is manual editing enough?
- **Source.** 2026-07-09 session — user flagged the backlog structure itself as an important design point before the file grows. Captured for tomorrow so nothing is lost.

## Landed — 2026-07-10

Struktur besprochen und umgesetzt. Konkret:

- **Ordner-Layout.** `docs/workflow-backlog/` mit einer Datei pro Item (`<NNN>-<slug>.md`), `index.md` als tabellarischer Übersicht, `_TEMPLATE_ITEM.md` als Copy-Paste-Vorlage.
- **Cross-References.** Backlog = Source of Truth. Memory `project_orchestrator_open_issues.md` schrumpft auf landed-Liste + Pointer, keine Content-Duplikation mehr. Neues `reference_workflow_backlog` Memory als Cold-Start-Pointer. Ships nur im project-template — kein neues Projekt hat so ein File.
- **Lifecycle.** On-demand konsultieren. Items collaborativ (nie silent). User entscheidet Prio, ich schlage vor. Exits: `done` (Code oder Konvention) oder `discarded` (Einzeiler-warum). Ich frage aktiv nach wenn Item complete wirkt.
- **Growth.** Filesystem-als-Index skaliert von selbst. Sprechende Slugs für Grep. IDs stabil ab Vergabe. Done-Items bleiben in-place (kein Archiv-Subfolder bei aktueller Größe). Vier-Zeilen-Vertrag über alle Prios, Bullet-Länge skaliert mit Prio.
- **Ritual.** Keine periodische Cadence. MEMORY.md-Pointer sorgt für Cold-Start-Sichtbarkeit. Keine Slash-Commands — manuelles File-Editing plus Konvention "Item hinzufügen = File-Op + Index-Zeile im selben Commit" reicht.

Vollständige Struktur-Konvention: siehe `index.md` → *Struktur & Konventionen*.
