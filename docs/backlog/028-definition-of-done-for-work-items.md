---
type: improvement
---

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

## Umsetzungsplan: Option H — sequenzielle Gate-Pipeline mit Design-Rückkehr

Konvergent aus mehreren Iterationen der Design-Diskussion Chat 2026-07-18/19. Evolution der Optionen (kurz, damit nachvollziehbar):

- **E (initial):** `ralph → docs_write → verify_docs → critic (full)` — Docs preemptiv geschrieben, kein sauberes Routing bei Docs-only-Failure.
- **E verfeinert:** `full` und `docs_only` Review-Modi, um bei Docs-Iterationen nicht komplett re-reviewen zu müssen. Cache-freundlich, aber Docs werden immer noch preemptiv geschrieben.
- **F:** dimensionierter Critic mit `failure_dimensions: [...]`-Array, parallel dispatch. Zu komplex, Routing wird schwammig, Multi-Dim-Handling nicht so relevant wie gedacht.
- **G:** Sequenzielle Gates statt dimensionierter Review. `ralph → struktur_check → docs_write → docs_gate`. Docs_write erst nach Struktur-Approval — löst Preemptive-Waste-Problem.
- **H (final):** G + Rückkehr-Kante vom Final-Gate zur Impl-Phase, weil Docs-Schreiben Design-Fehler enthüllen kann. Semantische Präzisierung: "approved" gibt's nur am Ende.

### Loop-Flow

```
Phase 1: ralph_loop (Impl + Test)
         └─ bestehend, iteriert bis Tests grün

Phase 2: struktur_check (Reviewer)
         ├─ pass  → Phase 3
         └─ fail  → Phase 1 mit Feedback

Phase 3: docs_write_phase (Actor)
         └─ Actor updated Docs basierend auf Diff.
            Actor darf abbrechen mit `design_issue_from_docs_attempt`
            wenn Verhalten nicht sauber beschreibbar ist → Phase 1.

Phase 4: final_approval (Reviewer, 3-Way Verdict)
         ├─ approve                    → commit
         ├─ reject route_to="docs"     → Phase 3 mit Feedback
         └─ reject route_to="design"   → Phase 1 mit Feedback
```

Ein Commit am Ende. "Approved" bedeutet exklusiv Phase-4-Approve — Phase 2 gibt nur einen Struktur-Pass ("darf weiter"), keinen Final-Segen.

### Structured Output für sauberes Routing

Reviewer nutzt Tool-Use / Function-Calling. Zwei Verdict-Schemas:

**Phase 2 (struktur_check):** binärer Ausgang
```python
{"pass": true} | {"pass": false, "reason": "..."}
```

**Phase 4 (final_approval):** 3-Way mit Kriterium-Enum
```python
{
  "approve": bool,
  "route_to": "docs" | "design" | null,  # null nur bei approve=true
  "criterion": "factual_error" | "missing_coverage" | "inconsistent_docs"
              | "leaky_abstraction" | "behavior_inconsistency"
              | "design_contradicts_other_docs" | "scope_beyond_mandatory",
  "reason": "..."
}
```

Der `criterion`-Enum zwingt den Reviewer sich explizit auf ein Kriterium zu committen — kein "irgendwo dazwischen"-Verdict möglich.

### Klassifikations-Kriterien im Reviewer-Prompt

Der Prompt für final_approval enthält die Zuordnung Kriterium → route_to:

```
route_to = "docs" wenn:
- factual_error         → Docs enthalten sachliche Fehler (Typo, falscher Befehl, falsche Version)
- missing_coverage      → Docs lassen ein Feature aus, das im Code existiert
- inconsistent_docs     → Docs widersprechen sich untereinander (README sagt X, CLAUDE.md sagt Y)

route_to = "design" wenn:
- leaky_abstraction              → Behavior nicht beschreibbar ohne Implementation-Details
- behavior_inconsistency         → Docs müssten widersprüchliches Verhalten dokumentieren
- design_contradicts_other_docs  → Code verletzt Verträge aus anderen Doku-Stellen
- scope_beyond_mandatory         → Änderung würde Files jenseits der Mandatory-Liste erfordern

Faustregel: Im Zweifel route_to = "design". Ein falsch-positiver Design-Flag kostet eine Ralph-Iteration
extra; ein übersehener Design-Fehler shippt broken code.
```

Design-First-Bias ist Absicht — asymmetrische Failure-Kosten (Design-Fehler shipping ist teurer als eine unnötige Ralph-Runde).

### Vier Guardrails gegen Reviewer-Fehlklassifikation

Klassifikation via LLM ist nicht 100% zuverlässig. Vier ineinandergreifende Mechanismen:

1. **Klare Kriterien im Prompt** (oben) — strukturierte Signale statt Prosa-Judgment.
2. **`criterion`-Enum-Zwang** — Reviewer muss sich explizit committen, keine unklaren Verdicts möglich.
3. **Cycle-Escalation**: `MAX_DOCS_CYCLES` (z. B. 2). Wenn Docs-Iteration den Zähler erreicht ohne Approve, force `route_to = "design"` — Evidenz dass Docs allein nicht das Problem sind.
4. **Actor-Fluchtstiege in Phase 3** — Actor darf docs_write abbrechen mit `design_issue_from_docs_attempt`, um Ralph mit einem Design-Hinweis anzustoßen. Fängt den Fall dass Actor beim Doku-Schreiben eine Inkohärenz entdeckt, bevor Phase 4 überhaupt drankommt.

Zusammen: **False-Positive-Design** ist billig (eine Ralph-Runde extra); **False-Negative-Design** (als Docs missklassifiziert) wird durch Cycle-Escalation systemisch gefangen.

### Kosten

| Szenario | Option H |
|---|---|
| **Happy Path** (Struktur-Check + Final-Approve first-try) | ~10-15k Tokens |
| **Interner Refactor** (Struktur pass, docs_write no-op, Final-Approve trivial) | ~8-13k Tokens |
| Docs-Iteration (Typo/Coverage) | ~15-20k |
| Design-Iteration (Struktur-Check fail oder Phase-4 route_to design) | ~20-30k |
| Design-durch-Docs (Cycle-Escalation oder Actor-Fluchtstiege) | ~25-35k (aber Design-Fehler gefangen — sonst wäre broken code committet) |

Wesentlich besser als F bei internen Refactors (kein preemptiver Docs-Check), vergleichbar bei Docs-Iterationen, teurer bei Design-durch-Docs — der Aufpreis der wirklich value liefert.

### Extensibilität — Modes-Muster für zukünftige Concerns

Das sequenzielle-Gates-Muster ist offen für weitere Gates. Beispielsweise Security als eigene Sequenz-Phase:

```
ralph → struktur_check → security_gate → docs_write → final_approval
```

Jedes neue Gate ist single-purpose, hat binäres oder 3-Way-Verdict, hat einen klaren Rückwärts-Sprung. Neue Gates fügen = Sequenz erweitern, kein Router-Casing-Zoo. Ohne dieses strukturelle Muster hätte Item 028 nur eine spezifische Lösung; mit ihm ist es ein Framework für alle künftigen orthogonalen Concerns (Security, Performance, Accessibility, …).

### Was noch offen ist / für die Umsetzung durchzudenken

- **Verankerungsort:** `workflow-implementation`-Skill (deklarativ) UND `orchestrator/loops.py` (enforcement) — wahrscheinlich beides parallel. Skill dokumentiert, Code führt aus.
- **Mandatory-Files-Liste:** Vorschlag Projekt-`CLAUDE.md` unter neuer Sektion, Default falls fehlend `[README.md, CLAUDE.md]`. Interaktion mit Struktur-Muster-Diskussion oben: bei Colocation ändert sich die Liste per Package.
- **Prompt-Caching in `orchestrator/claude.py`:** unbekannt ob explizit genutzt (`cache_control`-Marker) oder nur automatisch. Als 5-Min-Sichtprüfung am Session-Start.
- **`MAX_DOCS_CYCLES`-Wert:** 2 wahrscheinlich, aber empirisch zu justieren.
- **Feedback-Weiterleitung:** wenn Phase 4 `route_to="design"` sagt, wie kommt die `reason` als sinnvoller Prompt-Context in Ralph? Existierendes Ralph-Feedback-Muster wiederverwenden.
- **Interaktion mit Struktur-Mustern:** wenn Muster 1 (Generation) für API-Referenz eingeführt wird, entfällt `docs/api.md` als Mandatory. Reihenfolge Muster-Einführung ↔ Loop-Umbau durchdenken.
- **Ein Committed-Flag pro Phase im Log:** damit man beim Debug erkennt an welchem Gate ein Task gescheitert wäre / weitergeleitet wurde. Nice-to-have.
