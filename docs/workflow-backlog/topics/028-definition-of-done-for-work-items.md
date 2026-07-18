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

## Umsetzungsplan-Kandidat: Option E verfeinert (MVP-Skizze, noch nicht final)

Aus der Design-Diskussion Chat 2026-07-18 spätabends. Nutzer-Feedback: „das sieht schon recht gut aus aber wir müssen weiter daran arbeiten" — also: als Ausgangspunkt für die Morgen-Session, nicht als endgültiger Vertrag.

### Loop-Flow

```
1. write_tests_phase                       (bestehend)
2. ralph_loop bis Tests grün               (bestehend)
3. docs_write_phase                        (NEU — Actor updated Docs basierend auf Diff)
4. review(mode="full")                     (NEU — einzelner Critic-Call, alle drei Dimensionen)
5. Router in Python (aus Structured Output):
     approve                       → commit
     failure_dim = "code"/"tests"  → ralph_loop mit Feedback → zurück zu Step 3
                                     (weil Code neu, Docs müssen re-visited werden)
     failure_dim = "docs"          → docs_write_phase mit Feedback → Step 6
6. review(mode="docs_only")                (Focused-Prompt, Code + Tests bereits approved)
7. Router:
     approve                       → commit
     failure_dim = "docs"          → docs_write_phase, zurück zu Step 6
                                     (bis max_docs_critic_cycles erreicht)
```

Ein Commit am Ende (atomarer State, unveränderte Resume-Logik).

### Prompt-Modes

`review(mode)` ist eine Funktion mit identischem Präfix (Task-Content + Diff + Mandatory-Files) und unterschiedlichem Suffix:

- **`mode="full"`** — „Reviewe Code, Tests, Docs im Zusammenhang. Falls Ablehnung: nenne die Dimension die am kritischsten fehlt."
- **`mode="docs_only"`** — „Code und Tests sind bereits approved. Prüfe nur ob die Docs den Code jetzt korrekt beschreiben."

Strukturell EIN Critic-Component, zwei Prompt-Suffixe. Nicht zwei separate Critic-Loops mit eigenen `max_cycles`.

### Structured Output für sauberes Routing

Der Router lebt in Python, nicht im Prompt. Damit das funktioniert, gibt der Critic keine Prosa zurück, sondern nutzt Tool-Use / Function-Calling:

```python
tools = [{
    "name": "submit_verdict",
    "input_schema": {
        "properties": {
            "approve":           {"type": "boolean"},
            "failure_dimension": {"enum": ["code", "tests", "docs", null]},
            "reason":            {"type": "string"}
        }
    }
}]
```

Anthropic-API-erzwungene Struktur — kein Parse-Error möglich. Python routet deterministisch anhand `failure_dimension`.

### Kosten (grob)

| Szenario | Full-only Baseline | Verfeinert (mit `docs_only`) |
|---|---|---|
| Happy Path (first-try approved) | ~10–15k Tokens | Same |
| **Docs-Iteration** | ~20–30k (2× full) | **~13–17k** (full + docs_only, Cache-warm) |
| Code-Iteration | ~20–30k (2× full) | ~20–30k (Code-Kontext hat sich geändert, Cache invalid, Full nötig) |

Docs-Iterationen sind der häufige Fall der teuer wäre; hier greift die Ersparnis. Code-Iterationen bleiben teuer weil der Kontext dort inhaltlich neu ist — angemessen.

### Multi-dimensionale Fehler

MVP: iterativ. Critic gibt genau **eine** `failure_dimension` (die kritischste). Fix, nächste Runde findet die zweite. Später ausbaubar zu Liste, wenn nötig.

### Was noch offen ist / worüber wir weiterreden müssen

- **Verankerungsort:** Skill-Ebene in `workflow-implementation` (deklarativ, weich) vs. Code-Ebene in `orchestrator/loops.py` als explizite Phase-Funktion. Wahrscheinlich beides — Skill dokumentiert, Code enforced.
- **Mandatory-Files-Liste:** wo definiert? Vorschlag: Projekt-`CLAUDE.md` unter neuer Sektion, Default falls fehlend `[README.md, CLAUDE.md]`. Muss noch mit Struktur-Muster-Diskussion (oben) zusammengedacht werden — wenn wir Colocation (Muster 3) einführen, ändert sich die Liste per Package.
- **Prompt-Caching in `orchestrator/claude.py`:** heute unbekannt ob explizit genutzt (mit `cache_control`-Markern) oder nur automatisch. Als 5-Min-Sichtprüfung morgen früh.
- **Interaktion mit Ralph-Loop-Feedback:** wenn der Docs-Critic ablehnt, kriegt Docs-Write die Reason als Kontext — analog wie Ralph-Loop heute Critic-Feedback ins nächste Implement-Prompt einspielt. Existierendes Muster wiederverwenden.
- **Interaktion mit Struktur-Mustern (siehe Diskussion oben):** wenn wir gleichzeitig Muster 1 (Generation) einführen, entfällt `docs/api.md` als Mandatory-File komplett. Reihenfolge der Umsetzung durchdenken.
- **Kein finaler Vertrag**: Option E verfeinert ist der aktuelle beste Kompromiss aus Klarheit, Kosten und Robustheit. Ein weiterer Refinement-Zyklus in der nächsten Session ist explizit eingeplant.
