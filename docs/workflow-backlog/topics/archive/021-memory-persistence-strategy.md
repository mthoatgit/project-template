# P1 · Memory-Persistence — Migration ins Repo + Backup-Strategie

- **Symptom.** Load-bearing Entscheidungen aus laufenden Sessions leben in Claude's Auto-Memory unter `~/.claude/projects/.../memory/`. Der Ordner ist lokal, nicht versioniert, nicht gebackuped. Verschwindet die Maschine (neuinstalliert / kaputt / Verlust), verschwinden viele bisher getroffenen Konventionen und Präferenzen aus meiner Cold-Start-Sichtbarkeit — inklusive `feedback_workflow_style`, `feedback_semantic_naming`, `feedback_template_naming`, die aktiv Verhaltensregeln encoden. Gleiches Risiko gilt für `~/.claude/CLAUDE.md` (globales User-CLAUDE) und `~/.claude/skills/` — auch dort lebt Load-bearing Content ausschließlich lokal.
- **Impact.** In einer neuen Session ohne Memory würde ich bereits geklärte Regeln neu re-litigieren: Semantic-Naming-Concern vor Renames, Vier-Zeilen-Vertrag im Backlog, minimal-single-mechanism-Präferenz, Diskutiere-vor-Implementieren-Regel etc. Direkter Effizienz-Loss + Frust-Risiko + stille Regel-Erosion. Je länger wir die Zusammenarbeit ausschließlich session-basiert bauen, desto größer die Verlustexposition.
- **Proposed shape.** Zwei-Schichten-Best-Practice, in 2026-07-10 Session besprochen und als Richtung akzeptiert:
  - **Schicht 1 (strukturell, primär): Load-bearing Entscheidungen aus Memory heraus migrieren in versionierte, code-basierte Homes.** Konkret pro Memory-File:
    - `feedback_workflow_style` → `~/.claude/CLAUDE.md` (globales User-CLAUDE) unter neuer Sektion "Zusammenarbeitsregeln"
    - `feedback_semantic_naming` → gleiche Sektion in `~/.claude/CLAUDE.md`
    - `feedback_template_naming` → Projekt-`CLAUDE.md` oder relevantes `workflow-*/`-Skill (Konvention gehört an den Ort, an dem sie greift)
    - `project_orchestrator_open_issues` → Landed-Liste kann perspektivisch aus `git log` regeneriert werden; Deferred-Liste bereits nach Backlog migriert ✓; Memory-Eintrag schrumpft weiter zu Pointer + minimalem Landed-Snapshot
    - `project_orchestrator_dashboard_state` → gar keinen persistenten Home nötig, ist Session-Snapshot (stirbt in Stunden von selbst)
    - `reference_workflow_backlog` → README.md des Backlog dokumentiert Zweck + Konventionen bereits selbst ✓; Memory bleibt reiner Pointer, unkritisch bei Verlust
    - **Neue Konvention danach:** "Wenn ich eine neue Verhaltensregel lerne, gehört sie ins CLAUDE.md, nicht ins Memory." Memory wird für Ephemeres, State und Pointer, nicht für Load-bearing Rules.
  - **Schicht 2 (Backup, sekundär): `~/.claude/` gesamt unter Git-Version-Control.**
    - `git init` in `~/.claude/`
    - Privates Remote (GitHub-private / GitLab / Gitea / self-hosted)
    - Regelmäßig committen + pushen; Restore = clone
    - **Alternativen** (verworfen aber genannt):
      - Cloud-Sync (Dropbox/OneDrive/iCloud): zero-effort, aber Konflikt-Risiko bei Multi-Machine und keine echte Versionierung
      - Cronjob-Tarball zu Backup-Ziel: simpel, kein Diff-Trace, kein per-Change Kontext
    - Profis nehmen meist Git wegen Versionierbarkeit + Remote-Mirror + `git log`-Trail.
  - **Reihenfolge:** Schicht 1 zuerst (reduziert das Risiko sofort für die wichtigsten Regeln), Schicht 2 danach (systematischer Schutz für Rest + zukünftige Memories).
- **Source.** 2026-07-10 spät in Session — nach dem Backlog-Struktur-Redesign brachte User die Memory-Persistence-Frage auf. User fragte nach Best-Practices; die Zwei-Schichten-Antwort wurde gemeinsam als Richtung bestätigt. User explizit: *"gehe sicher dass wir hier morgen genauso weitermachen können, priorisiere es als erstes für den nächsten termin"*. Item entstand aus dem Flow, war vorher nicht auf dem Backlog.

## Session-Kontext — Wiedereinstiegspunkt für nächste Session

**Status:** Konzept + Best-Practice besprochen, konkrete Migration noch nicht gestartet. Item wurde explizit gefiled um Kontinuität bei Session-Ende sicherzustellen.

**Was schon geklärt ist (nicht neu diskutieren):**
- Zwei-Schichten-Ansatz ist als Richtung akzeptiert
- Reihenfolge: Schicht 1 zuerst, Schicht 2 danach
- Audit-Table der aktuellen Memory-Files vorhanden (in Proposed shape oben)
- Cloud-Sync + Tarball-Backup als Alternativen verworfen; Git+Remote ist die Präferenz

**Konkrete erste Schritte für nächste Session:**
1. **Sektions-Struktur klären.** Neue H2 "Zusammenarbeitsregeln" in `~/.claude/CLAUDE.md`, oder bestehende Sektion erweitern? Aktuell hat das globale CLAUDE.md "How I work", "Language", "Template Files", "Workflow Skills", "Slash Commands", "Strict Behavior Rules" — Verhaltensregeln könnten unter "Strict Behavior Rules" oder als eigene Sektion.
2. **Pilot-Migration mit `feedback_workflow_style`.** Content ins CLAUDE.md, Memory-File löschen, MEMORY.md-Index aktualisieren. Ende-zu-Ende einmal durchziehen um die Migration-Mechanik zu erproben.
3. **Bei glattem Pilot restliche `feedback_*` Files mitmachen** (`feedback_semantic_naming`, `feedback_template_naming`).
4. **Danach Schicht 2 designen und starten:** Remote-Wahl (GitHub-private als Default?), `.gitignore` fürs `~/.claude/`-Repo (session-scoped Logs, cache-Dirs ausschließen?), initial commit + push, Klärung ob Multi-Machine geplant ist.

**Nicht vergessen:**
- Trade-off Schicht 2: bei Multi-Machine-Nutzung Sync-Konflikte möglich — User sanity-checken (aktuell eine Maschine)
- Sensitive Content in Memories? Vor Push zu Remote screenen. Aktuell nichts kritisches drin, aber Governance-Regel etablieren
- Nach Migration: aktive Cleanup-Runde durch die verbleibenden Memories, was noch redundant ist
- Diese Datei sich selbst nicht vergessen: nach Umsetzung Status `done`, Move nach `topics/archive/`

## Landed — 2026-07-11

Beide Schichten umgesetzt in einer Session.

**Schicht 1 — Content-Migration ins versionierte CLAUDE.md.**

- `feedback_workflow_style` → neue H1 "Collaboration Style" in `~/.claude/CLAUDE.md`, vier Subsections (discuss-before-implement · minimalism-beats-defence-in-depth · name-real-trade-offs · brief stack context). Regel "respect workflow rituals" gedroppt — bereits durch bestehende "Strict Behavior Rules: NEVER skip phases" abgedeckt.
- `feedback_semantic_naming` → weitere Subsection unter Collaboration Style (flag semantic naming concerns before renames). **Update 2026-07-11 (Post-Migration-Assessment):** Diese Subsection wieder aus CLAUDE.md entfernt — der T→F Rename wurde im selben Session zurückgerollt, es ging nichts in Production kaputt, und eine permanente Regel für 30 Minuten Process-Friction verletzt "minimalism beats defence-in-depth". Memory-File selbst blieb gelöscht.
- `feedback_template_naming` → **Decision 2D** (spontan im Session-Verlauf gewählt statt geplanter 2A): One-liner ans Ende der bestehenden "Template Files"-Sektion angehängt statt project-CLAUDE.md, weil (a) die Konvention nicht projektspezifisch ist sondern für jedes scaffolded Projekt gilt, (b) global CLAUDE.md die Dual-Konvention ohnehin schon beschreibt — es fehlte nur der "don't propose unifying" Meta-Guard.
- **Neue Governance-Rule** unter Collaboration Style: "Prefer CLAUDE.md over auto-memory for behavioral rules" — verhindert dass zukünftige Verhaltensregeln wieder in unversionierter Memory landen.
- Memory-Files gelöscht: `feedback_workflow_style.md`, `feedback_semantic_naming.md`, `feedback_template_naming.md`. `MEMORY.md`-Index bereinigt. Dangling `[[…]]`-Backlinks in 4 anderen Memory-Files gepruned.

**Schicht 2 — `~/.claude/` unter git.**

- **Entdeckung während Umsetzung:** `~/.claude/` war bereits am 2026-05-21 als git-Repo initialisiert mit Remote `git@github.com:mthoatgit/dotfiles-claude.git` (private). `.gitignore` implementiert bereits das Best-Practice-Muster: **default-deny + explicit whitelist + belt-and-suspenders blacklist** (Credentials, projects/, sessions/, history.jsonl, plugins/, cache/ explizit denied selbst wenn Whitelist mal slippt). Whitelisted: `.gitignore`, `README.md`, `CLAUDE.md`, `settings.json`, `skills/**`, `commands/**`. Layer-2-Konzept aus Item 021 war also bei Fileing bereits partiell existent — Item wusste das nicht.
- **Übrig-gebliebene Arbeit:** 7 Wochen Drift committen und pushen. Zwei Commits:
  - `docs(claude): migrate collaboration-style rules from auto-memory` — Layer-1-Content.
  - `chore: catch up 7 weeks of workflow-skill, command and settings drift` — akkumulierte Skill-, Command- und settings.json-Änderungen.
- Beide gepusht auf `origin/main`. Restore-via-Clone funktioniert jetzt für alles unter der Whitelist.

**Flag für später (nicht Blocker):** `settings.json` enthält absolute Windows-Pfade (`C:\Program Files\nodejs\...`, `C:\Users\mthor\...`) — bei Clone auf andere Maschine kaputt. Maschinen-spezifisches gehört in `settings.local.json` (bereits gitignored). Separates Backlog-Item wenn Multi-Machine relevant wird.

**Was NICHT gemacht wurde** (bewusst außer Scope für 021):
- `project_orchestrator_open_issues` weiter schrumpfen (landed-Liste könnte aus `git log` regeneriert werden). Nicht load-bearing genug für sofortigen Aufwand.
- `project_orchestrator_dashboard_state` unangetastet — stirbt als Session-Snapshot in Stunden/Tagen von selbst.
- `reference_workflow_backlog` unangetastet — bereits reiner Pointer, konsistent.
