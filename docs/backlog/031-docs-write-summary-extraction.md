---
type: improvement
---

# P3 · Docs-Write-Phase: inhaltliche Summary statt Konstante

- **Symptom.** `loops.py::critic_loop` printet nach der Docs-Write-Phase auf dem Happy-Path nur eine konstante Zeile `[OK] docs updated` (Fix für [[030-option-h-e2e-followups]] #3). Das ist bereits eine deutliche Verbesserung gegenüber der vorherigen kompletten Stille, aber die Aussage ist inhaltsleer — sie sagt nicht *ob* Files geändert wurden, *welche*, oder ob der Actor entschieden hat dass nichts zu tun war (siehe [[030-option-h-e2e-followups]] Insight #9: „Docs-Write-Output hat keinen expliziten Success-Signal"). Beispiel-Actor-Antwort aus dem 2026-07-19 E2E-Run: „README.md already documents the import correctly and makes no stale claims about `farewell`, so no changes needed there. CLAUDE.md's Public API section is now in sync with the new `farewell` implementation." — enthält alles was man wissen will, wird aber nicht ins Progress-Log gehoben.
- **Impact.** Beim Zurückschauen auf einen Task-Run kann man nicht aus dem Progress-Log alleine sagen ob docs_write:
  - konkret welche Files geändert hat (README, CLAUDE.md, beide, keine),
  - inhaltlich beschreibt was geändert wurde,
  - oder als reiner No-Op durchlief.
  Für Auditing / Debugging bei Class-A-Bug-Analyse (analog B03-Story in Item 028) sind das genau die Signale die man haben will. Aktuell muss man zum vollen `orchestrator-<timestamp>.log` gehen, wo die Actor-Antwort inline mit `│ `-Prefix liegt.
- **Proposed shape.** Zwei komplementäre Ansätze:
  1. **Heuristische Extraktion.** Nach `run_claude(docs_prompt, ...)` letzte nicht-leere Nicht-JSON-Zeile der Actor-Antwort ziehen und im `[OK]`-Print statt „docs updated" verwenden. Truncation bei z.B. 200 Zeichen mit `…`-Suffix. Fallback auf Konstante wenn Extraction leer.
  2. **Struktur im Actor-Prompt erzwingen.** Prompt so ändern dass Actor am Ende einen **kurzen Summary-JSON-Block** produziert, ähnlich Struktur-Check-Verdict: `{"changed": ["CLAUDE.md"], "unchanged": ["README.md"], "summary": "…"}`. Parser extrahiert und printet. Robuster als Heuristik, aber ändert das Actor-Contract — muss auch in `bug_variant.py` gespiegelt werden. Passt inhaltlich gut zu [[029-tool-use-for-orchestrator-reviewers]] falls das eines Tages umgestellt wird.

  Empfehlung: **Ansatz 1 zuerst** — reine UI-Improvement, kein Contract-Change. Falls sich rausstellt dass Heuristik zu unzuverlässig ist (leere Antworten, nur Prosa ohne konkrete File-Nennung), auf Ansatz 2 upgraden.

  Testing: neuer Unit-Test in `test_loops.py` der prüft dass die extrahierte Summary im Progress-Log auftaucht wenn Actor-Antwort einen sinnvollen Inhalt hat.
- **Source.** Chat-Session 2026-07-19 nach E2E-Run. Nutzer nach Vorschlag heuristisch-vs-konstant: „mir reicht erstmal dieses docs updated aber schreibe mal einen backlog item für das thema das können wir uns dann später anschauen" — explizite Deferral, konstante Version bleibt als Minimum drin.
