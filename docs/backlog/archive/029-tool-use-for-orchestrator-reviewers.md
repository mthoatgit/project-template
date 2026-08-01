---
type: improvement
status: dropped
---

# P3 · Tool-Use / Function-Calling für Orchestrator-Reviewer statt JSON-in-Text

- **Symptom.** Die in [[028-definition-of-done-for-work-items]] verankerte Option-H-Pipeline (Struktur-Check + Final-Approval) wird pragmatisch mit **JSON-in-Text**-Verdicts umgesetzt: Prompt instruiert Claude einen JSON-Block ans Ende der Antwort zu setzen, Parser fischt ihn per Regex heraus (`json.loads` mit Fallback-Defaults). Failure-Modi existieren strukturell: Claude vergisst den Block, wrapped ihn in Markdown-Fences ` ```json `, weicht vom Enum ab, produziert Preamble-Prosa die Parser irritiert. Heute abgefangen durch robuste Parser + Design-First-Bias als Default, aber nicht garantiert.
- **Impact.** Klassifikations-Fehler in Phase 4 (`route_to`, `criterion`) kosten pro Fall eine Cycle-Runde extra oder — im Worst Case — Feh-Approval mit Docs-Drift die durchrutscht. Skalierungs-schmerzhaft: je mehr Gates die Sequenz kriegt (Item 028 erwähnt Extensibilität für Security, Performance, Accessibility), desto mehr JSON-Contracts hängen an Prompt-Instruktions-Disziplin statt an API-Enforcement.
- **Proposed shape.** Umstellung der Reviewer-Aufrufe (Phase 2 `struktur_check`, Phase 4 `final_approval`) auf **Tool-Use / Function-Calling** auf API-Ebene:
  1. **Neue API-Client-Schicht** neben oder statt `orchestrator/claude.py`. Direktes HTTP an Anthropic Messages API mit `tools=[...]`-Parameter, Response als `tool_use`-Content-Block mit garantiert schema-konformem Input.
  2. **Kaskade-Entscheidungen** die dabei mit hängen:
     - **Auth-Modell:** heute läuft alles über `claude`-CLI mit dem User-Abo. Direkt-API braucht separaten `ANTHROPIC_API_KEY` + eigene Billing. Muss der Orchestrator beide Modi können (CLI für Actor-Calls, API für Reviewer)? Oder komplett auf API umziehen?
     - **Session-Limit-Handling:** `claude.py::handle_session_limit` fängt heute CLI-Ausgaben ab und pausiert bis Reset. API hätte andere Signale (429 mit `retry-after`-Header, o.ä.) — muss neu implementiert werden.
     - **Guardrail-Modell:** `subprocess_settings.json` mit `permissions.deny` blockt heute git-writes und `orchestrator/`-Writes (REQ-39, REQ-41) auf CLI-Ebene. Bei API-Direktzugriff mit Tool-Use gilt das nicht — Tool-Use hat kein permissions-Konzept, die "Tools" die der Model ausführen darf werden explizit deklariert. Anderer Enforcement-Weg.
     - **Streaming:** heute streamt `run_claude` Zeile-für-Zeile in den Log (`sys.stdout.write(f"  │ {raw_line}")`). API mit Tool-Use hat eigenen Streaming-Modus — funktioniert, aber muss ein anderer Weg gebaut werden.
  3. **Hybrid-Möglichkeit:** Actor-Phasen (Ralph, docs_write) bleiben auf CLI (weil Actor die vollen Tool-Rechte + Filesystem-Zugriff braucht → CLI-Modell passt). Reviewer-Phasen (struktur_check, final_approval) auf API (weil Reviewer nur Diff lesen + strukturiertes Verdict zurückgeben → API mit Tool-Use passt). Zwei Aufruf-Modi im selben Orchestrator, klar getrennt. Schafft aber Komplexität + zweite Billing-Quelle.
- **Source.** Chat-Session 2026-07-19 im Anschluss an die Option-H-Umsetzungs-Planung. Nutzer-Zitate:
  - „variante b klingt sehr robust und scheint mir die bessere lösung zu sein richtig? falls ja dann erstelle nochmal eine backlog item dafür damit wir uns im anschluss anschauen können. wir bleiben erstmal bei variante a" — Auslöser, expliziter Aufschub.
  Verwandt: 028 (Option-H-Pipeline, in Umsetzung — bleibt bei JSON-in-Text bis dieses Item angegangen wird).

## Dropped

**Dropped 2026-08-01.** Reason: backlog reset after the skeleton/ restructure (034) — not evaluated individually.
