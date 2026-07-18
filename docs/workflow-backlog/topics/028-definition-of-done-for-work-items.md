# P2 · Definition-of-Done-Checkpoints im Implementation-Loop — Impl → Test → Docs

- **Symptom.** Der `critic_loop` im Orchestrator kennt heute die Phasen `[Write Tests] → [Implement] → [Verify Tests] → [Critic]`. Was strukturell fehlt: ein expliziter Docs-Check-Schritt, der prüft ob alle Doku im Repo, die das geänderte Verhalten beschreibt, mit-aktualisiert wurde. Bei B03 im orchestrator-dashboard (Commit `5c4e938`) landete der Code-Fix, aber `README.md`, `CLAUDE.md` und `backend/tests/test_t03_lan_binding_and_start_commands.py::BACKEND_START_COMMAND` blieben stale — vier Nach-Commits per Hand nötig (`aa7d676`, `0b918e9`, `bde654b`, `2d2c697`). Zusätzlich: Task-Loops haben denselben Fehlermodus, weil der Actor-Prompt für Task und Bug identisch ist.
- **Impact.** Jeder Class-A-Fix (Task oder Bug) läuft heute Gefahr, Doku-Divergenz zu erzeugen. Der Actor ist scope-diszipliniert (Critic warnt vor Scope-Creep, siehe B03-Cycle-0), aber Doku-Konsistenz ist strukturell nicht als Verpflichtung im Loop verankert. Die 027-Lösung (Filer-provided Affected Surface) wurde am selben Abend zurückgerollt — sie verlangt Wissen zum falschen Zeitpunkt (Filer kennt beim Filing typischerweise weder Root Cause noch betroffene Doku-Stellen). Details in [[027-bug-file-affected-surface-section]] unter „Reverted — 2026-07-18".
- **Proposed shape.** Nutzer hat die Richtung im Chat gewählt: **DoD als sequenzielle Checkpoints** (nicht als Property-Liste), einheitlich für Task- und Bug-Loops.
  1. **Drei Checkpoints, sequenziell, mit klarem Pass/Fail:**
     - **Impl-Checkpoint** — Code-Änderung ist gemacht. (Heute implizit über die `[Implement]`-Phase abgebildet.)
     - **Test-Checkpoint** — Regression-Test / Task-Test existiert und ist grün, kein anderer Test regrediert. (Heute über `[Verify Tests]` + Full-Suite-Run.)
     - **Docs-Checkpoint (NEU)** — Actor sucht aktiv nach Signaturen des geänderten Verhaltens im Repo (grep über alte Wortlaute/Konstanten/Kommandos) und aktualisiert jede Fundstelle. Filer-Wissen ist NICHT vorausgesetzt.
  2. **Verankerungsort:** in `~/.claude/skills/workflow-implementation/SKILL.md` (der Skill der die Actor-Prompts für beide Loop-Varianten formt). Zwei mögliche Umsetzungsebenen:
     - **Skill-Ebene (deklarativ, weich):** DoD steht als Verpflichtung im Skill, Actor führt sie aus, Critic prüft am Ende. Einfach zu iterieren.
     - **Code-Ebene (Phase im Orchestrator):** neue `[Verify Docs]`-Phase in `orchestrator/loops.py` mit eigenem Prompt, direkt vor dem `[Critic]`-Review. Erzwingbarer und lokalisierter Fehler bei Rot. Aufwendiger.
     Entscheidung mit Umsetzung koppeln.
  3. **Docs-Check-Mechanik (der eigentlich interessante Teil, zu klären in der Follow-up-Session):**
     - Wie leitet der Actor die Grep-Signatur ab? Aus dem Diff? Aus dem Bug-Symptom? Aus dem Task-Goal?
     - Was zählt als „Fundstelle beschreibt das Verhalten"? Semantisch ähnliche Prosa vs. wörtliches Match?
     - Umgang mit False Positives (Grep findet was, aber es beschreibt anderes Verhalten)?
     - Escalation wenn Actor Doku findet die er nicht sicher ändern kann → `action needed`?
  4. **Affected Surface als Konzept: verworfen.** Die Idee einer Filer-provided Datei-Liste (027) ist strukturell fehl am Platz — Filer hat das Wissen nicht. Der Docs-Checkpoint ersetzt die Absicht. Kein separates optionales Feld nötig; die Faktenlage steht im Fix-Commit-Diff.
- **Source.** Chat-Session 2026-07-18. Kernzitate zur Entscheidungsfindung:
  - „ich denke darüber nach einen dod also checkpoints für die implementierung einer task oder bug einzubauen quasi implementierung, test überprüfen und schauen ob alle docs up to date sind nach der änderung" — Ursprung der Checkpoint-Idee, insbesondere Docs-Check als expliziter Schritt.
  - „die frage ist wie affect surface tatsächlich ins ticket gelangt. ich stelle einen fehler fest wie soll dann die affect surface vorher bekannt sein?" — führte zum 027-Rollback (Chicken-and-Egg-Problem).
  - „ja option 1 affect surface kann weg." — Bestätigung des Rollbacks in derselben Session.
  Verwandt: 027 (Bug-Template Affected Surface, done + reverted — dieselbe Session), 020 (workflow-bugs Skill, done — hat B-Support ohne Docs-Check-Verankerung eingeführt).
