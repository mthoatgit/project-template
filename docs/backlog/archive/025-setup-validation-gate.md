---
type: improvement
status: dropped
---

# P2 · Setup-Validation-Gate vor Orchestrator-Start (README + check-env.py + Skill-Hooks)

- **Symptom.** Fehlende Maschinen-Voraussetzungen fallen erst *während* der Implementierung auf, nicht davor. Am 2026-07-18 in `orchestrator-dashboard` konkret geworden: der in `CLAUDE.md` dokumentierte Backend-Startbefehl (`uvicorn backend.src.main:app`) scheitert dreifach (uvicorn nicht im PATH, Import-Layout inkonsistent zum Startpfad, Target-Path-Fallback funktioniert nur aus einem CWD, in dem der Startbefehl gar nicht läuft). Der Bug B04 in orchestrator-dashboard fixt die akute Reibung — aber es gibt keinen strukturellen Gate, der solche Maschinen-vs-Projekt-Mismatches *vor* dem Loop fängt, und keine Konvention, die die Setup-Doku bei jedem neuen Task/Bug auf Aktualität prüft.
- **Impact.** Jede neue Session, jeder neue Rechner riskiert dieselbe stumme Reibung. Der Bug-Workflow fängt sie retrospektiv nach verlorener Debug-Zeit; ein proaktiver Gate fängt sie deterministisch vor dem ersten Testrun. Zusätzlich: Setup-Doku driftet an, wenn Prereqs beim Hinzufügen neuer Deps nicht mit-editiert werden, und man merkt es erst wenn es zu spät ist.
- **Proposed shape.** In Chat-Session 2026-07-18 destilliert:
  - **Pro Projekt (Struktur, die project-template als Skeleton spendieren kann):**
    - README-Setup-Abschnitt in Prosa — authoritativ für Menschen, "wie richte ich das ein".
    - `scripts/check-env.py` — rein mechanische Prüfungen als Python-Code (`check("uvicorn on PATH", cmd=[…])`), still bei Erfolg, klarer Fehler bei Fail. Standalone aufrufbar für Debug ("warum geht das plötzlich nicht").
    - `scripts/start-implementation.py` — winziger Wrapper: (1) `check-env.py` ausführen, bei Fehler `sys.exit(1)` mit klarer Meldung; (2) sonst Args unverändert an `python -m orchestrator` durchreichen. Kein Env-Wissen im Orchestrator selbst — der bleibt framework-agnostisch (analog `scripts/test.py`).
    - Projekt-`CLAUDE.md` dokumentiert den Wrapper als *einzigen* Einstiegspunkt für die Implementierungsphase (nicht direkt `python -m orchestrator`).
    - Projekt-`CLAUDE.md` enthält Konvention: "README-Setup-Abschnitt UND `scripts/check-env.py` werden im *selben Commit* aktualisiert. Nie nur eins von beiden."
  - **In `dotfiles-claude` (damit alle künftigen Projekte das mitbringen und Setup nicht bei jedem Neuprojekt neu erfunden wird):**
    - `workflow-architecture` — Schritt: aus den Stack-Entscheidungen initialen README-Setup-Abschnitt + `scripts/check-env.py` ableiten und anlegen. Bei Stack-Änderungen anpassen.
    - `workflow-tasks` — expliziter Prüfschritt beim Schreiben *jedes* Tasks: "Führt dieser Task eine neue Dep/ein neues Tool ein? Wenn ja, README-Setup + `check-env.py` im selben Commit mit-editieren."
    - `workflow-bugs` — analog zu Tasks.
  - **Ebenen-Rollenverteilung sauber halten:** Skript = Enforcement-Gate. AI (bei Task/Bug-Schreiben) = Discovery/Vorschlag. AI-Discovery *während* der Implementierung = Sicherheitsnetz für das, was durch Architecture/Tasks/Bugs durchgerutscht ist, nicht die primäre Quelle.
  - **Explizit ausgeschlossen:** keine LLM-Prüfung *im* Check-Loop (Determinismus + Latenz + Offline-Bruch). Keine separate `docs/prerequisites.md`-Datei (würde nur dritte Quelle der Wahrheit erzeugen — Prosa im README + Code in `check-env.py` reicht).
- **Source.** Chat-Session 2026-07-18 in `orchestrator-dashboard`. Trigger war Bug B04 (Backend cannot be started as documented) — dort reine Fix-Arbeit, die systemische Frage "wie fangen wir sowas beim nächsten Projekt schon vor der ersten Reibung" landet hier. Naming `start-implementation.py` bewusst gewählt (nicht `run-orchestrator.py`), weil es sich mit der Phasen-Sprache des Workflows deckt; Kollision mit dem `start-epic`-Skill semantisch ok (eins ist Skill, das andere ist Script).

## Dropped

**Dropped 2026-08-01.** Reason: backlog reset after the skeleton/ restructure (034) — not evaluated individually.
