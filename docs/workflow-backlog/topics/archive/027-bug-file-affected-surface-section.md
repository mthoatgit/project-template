# P2 · Bug-File hat keine „Affected Surface"-Sektion — Actor scoped zu eng, Doku driftet

- **Symptom.** Bug-Files enthalten heute keine explizite Aufzählung, welche Flächen (Code, Tests, Docs) der Fix atomar anfassen muss. Der Actor im Orchestrator-Loop lädt das komplette Bug-File als Prompt-Content und leitet den Scope aus `## Reproduction`, `## Root Cause`, `## Fix` ab — alle drei sind narrativ und Code-zentriert. Konkret bei B03 heute (`5c4e938`): fixiert wurde `backend/src/config.py`, aber `README.md`, `CLAUDE.md` und `backend/tests/test_t03_lan_binding_and_start_commands.py::BACKEND_START_COMMAND` blieben unverändert — obwohl alle drei genau den Startbefehl dokumentierten, den das Bug-Symptom als kaputt beschreibt. Die Konsistenz-Arbeit landete danach in vier separaten Commits (`aa7d676`, `0b918e9`, `bde654b`, `2d2c697`).
- **Impact.** Jeder Bug über „documented behavior doesn't work" trägt dieses Muster: Code-Fix landet im Loop, Doku und Test-Konstanten mit derselben Behavior-Beschreibung bleiben stale. Der Critic hat im B03-Loop sogar explizit vor Scope-Creep gewarnt (Cycle 0, Punkt 5), was den Actor korrekt darauf trainiert, eng zu bleiben. Ohne eine strukturell vorab festgelegte Fläche-Liste ist der Actor gefangen zwischen „bleib eng" (Critic-Signal) und „halte alles konsistent" (Realität nach dem Fix). Die Auflösung heute war menschliches Nacharbeiten außerhalb des Loops — genau das, was der Orchestrator-Loop eigentlich vermeiden sollte.
- **Proposed shape.** Zweiteilige Änderung, gemeinsam im Rahmen der Sitzung 2026-07-18:
  1. **In project-template** — `docs/tasks/_TEMPLATE_BUG.md` um eine Sektion `## Affected Surface` erweitern, positioniert **zwischen `## Reproduction` und `## Root Cause`**. Wird beim Filing befüllt (nicht beim Handling), listet drei Kategorien:
     - **Code:** Dateipfade + kurze Angabe was ändert
     - **Tests:** Dateipfade + Konstanten/Assertions, die mitgehen müssen
     - **Docs:** README-Sektionen, CLAUDE.md-Blöcke, andere Doku, die dasselbe Verhalten beschreibt
     Der Text erklärt: „Diese Zeilen müssen im Fix-Commit alle mit editiert werden. Fehlt eine Zeile hier, wird der Actor sie nicht anfassen — die Divergenz bleibt."
  2. **In dotfiles-claude** — `~/.claude/skills/workflow-bugs/SKILL.md`:
     - „Bug file structure" um die neue Sektion ergänzen
     - Class-A-Handling-Protokoll um eine Regel „fix touches exactly the surfaces listed" ergänzen
     - „Rules"-Block am Ende um dieselbe Regel ergänzen
  3. **Keine Änderung am Orchestrator-Prompt nötig.** Der Actor liest das ganze Bug-File als `content` — die neue Sektion wird von selbst sichtbar. Wenn sich in der Praxis zeigt, dass Prompt-Boost nötig ist, ist das ein Follow-up.
- **Source.** Chat-Session 2026-07-18, B03-Orchestrator-Run in `orchestrator-dashboard` und anschließende Konsistenz-Retrospektive. Verwandt: 002 (Root Cause + Fix bleiben nach Bugfix leer — dieselbe Kategorie „Bug-File-Sektionen, die Disziplin brauchen"), 020 (workflow-bugs Skill, done — hat B-Support eingeführt, die Scope-Disziplin aber offen gelassen).

## Landed — 2026-07-18

Beide Änderungen wie vorgeschlagen umgesetzt, keine Abweichung vom Proposed shape:

- **`docs/tasks/_TEMPLATE_BUG.md`** (project-template): neue Sektion `## Affected Surface` zwischen `## Reproduction` und `## Root Cause` mit drei Kategorien (Code / Tests / Docs) und Placeholder-Text, der die Filing-Zeit-Semantik erklärt („Actor uses this as atomic scope; missing row → stale after fix").
- **`~/.claude/skills/workflow-bugs/SKILL.md`** (dotfiles-claude): drei chirurgische Ergänzungen — (a) neuer Bullet in „Bug file structure" für die Sektion, (b) Class-A-Handling-Protokoll Step 6 umformuliert auf „Fix every surface listed", (c) neue Rule im Rules-Block am Ende, symmetrisch zur bestehenden „regression test in the same commit"-Rule.
- **Kein Orchestrator-Prompt-Change nötig** — der Actor lädt das ganze Bug-File als Prompt-Content, die neue Sektion wird von selbst sichtbar. Wenn sich in der Praxis zeigt, dass ein Prompt-Boost nötig ist (etwa: der Actor ignoriert die Sektion trotz Sichtbarkeit), ist das ein separates Follow-up.

Erster Testfall für die neue Sektion wird der nächste Class-A-Bug in irgendeinem Projekt sein — ex-post-facto Nachziehen für B03 lohnt sich nicht (der Fix ist schon durch, die Konsistenz-Commits ebenfalls).
