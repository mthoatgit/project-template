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

## Ergänzende Diskussion: Struktur-Muster gegen Doku-Drift (Chat 2026-07-18 spätabends)

Nutzer-Frage: „wie machen es die profis von anthropic oder claude code experten … was ist der best practice?" — führte zur Erkenntnis, dass DoD-Checkpoints (loop-seitig) und Struktur-Muster (docs-seitig) **komplementär** sind und gemeinsam mehr fangen als eins allein. Keiner der Ansätze eliminiert Drift; zusammen minimieren sie.

### Was von Anthropic/Claude Code öffentlich sichtbar ist

- `CLAUDE.md`-Konvention (Anthropic's eigene Erfindung — Instructions leben in der Codebase, versioniert, near-code)
- Skills als reusable Prompts (analog zu `~/.claude/skills/`)
- Public-Doku `docs.claude.com/claude-code` separat von Feature-Code gepflegt (traditionelles Docs-Team-Setup)

Interne Prozesse nicht bekannt — offen für Session-Start-Option (a) unten.

### Industry-Muster, sortiert nach Effektivität für dieses Problem

| # | Muster | Kernidee | Vorteil | Nachteil |
|---|---|---|---|---|
| 1 | **Generation** | Doku wird aus Code erzeugt (OpenAPI aus FastAPI, JSON-Schema aus Pydantic, `--help` aus argparse) | Kann strukturell nicht driften | Nur für strukturierte Dinge, nicht Prosa |
| 2 | **Tests-on-Doc-Text** | Test asserted auf dokumentierten Text/Befehl (T03-Prinzip) | CI-enforced, Vergessen unmöglich | Brüchig bei Wortlaut-Änderungen |
| 3 | **Colocation** | Doku wandert näher an Code (Package-READMEs, Module-Docs) | Kognitive Nähe beim Editieren | Doku-Fragmente, keine „eine Story" |
| 4 | **Anchor-Comments** | `// See docs/foo.md#bar` im Code | Billig, macht Verbindung explizit | Manuelle Disziplin, stale bei Umzügen |
| 5 | **Executable Code-Blocks** | Code-Blocks in Docs laufen im CI (Rustdoc, mdx) | Automatisch verifizierbar | Setup-Overhead, nur für Ausführbares |
| 6 | **PR-Checklisten** | „[ ] Docs updated?" im PR-Template | Menschen-Moment | Häkchen-Blindheit |

### Empfehlung für Setup dieser Größenordnung

- **Sofort billig (jetzt anfangbar):**
  - Muster 4 (Anchor-Comments) — ein Kommentar pro relevanter Config-Konstante, der auf die Doku-Sektion zeigt
  - Muster 2 systematisieren — Konvention „jeder dokumentierte User-facing Befehl hat einen Test der auf den Wortlaut assertiert" (T03 ist der Prototyp, in `workflow-tests`-Skill als Regel verankern)
- **Mittlerer Aufwand:**
  - Muster 1 — FastAPI's OpenAPI-Output → Skript zu Markdown, CI-Check dass generierte Doku aktuell ist; dann existiert `docs/api.md` gar nicht als handgeschriebene Datei
  - Muster 3 — `backend/README.md` + `frontend/README.md` für Setup-Instructions; Root-README verweist nur
- **Größerer Aufwand:** Muster 5 wahrscheinlich Overkill für diese Projektgröße; erst bei viel Tutorial-Content lohnend

### Beziehung zu DoD-Checkpoints (dem Hauptvorschlag des Items)

Zwei Verteidigungsebenen, unterschiedliche Failure-Modi:

- **Struktur (Muster 1–5)** macht Drift schwerer oder strukturell unmöglich (generiert, verlinkt, colokalisiert, im Test gepinnt)
- **DoD-Checkpoints (Kernvorschlag oben)** fangen ab was durchrutscht — den Rest, den Struktur nicht deterministisch abfängt

Das ist die seltene Ausnahme, wo Belt-and-Suspenders gerechtfertigt ist: Muster 1–5 sind punktuell, Checkpoints sind flächendeckend, keine ersetzt die andere komplett.

### Zwei Optionen zum Session-Start

- **(a) Erst Empirie:** WebFetch von `github.com/anthropics/claude-code` und `docs.claude.com/claude-code` — konkret prüfen wie Anthropic seine eigene Codebase-Doku organisiert, statt aus dem Bauch zu entscheiden. ~10 Minuten Aufwand. Ergibt Datenbasis für die Entscheidung, welche Muster in project-template als Konvention landen.
- **(b) Direkt in die Entscheidung:** aus dem obigen Bild wählen welche Muster adoptiert werden. Weniger Empirie, schnelleres Vorankommen. Passt wenn du für dein Setup schon ein Gefühl hast, was zu dir passt.

Beide legitim. Entscheidung morgen früh.
