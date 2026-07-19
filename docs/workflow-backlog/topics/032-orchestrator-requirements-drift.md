# P2 · `orchestrator-requirements.md` beschreibt Post-028 Verhalten inkonsistent

- **Symptom.** `docs/orchestrator-requirements.md` REQ-15 bis REQ-20 unter der Sektion „Critic-Actor pattern" beschreiben das Verhalten VOR [[028-definition-of-done-for-work-items]]:
  - REQ-15/16: „an adversarial Critic reviews … evaluates idiomatic approach …" (heute: drei sequenzielle Gates)
  - REQ-17: „The Critic outputs `APPROVED` or `REJECTED` with specific design-level concerns" (heute: JSON-Verdicts mit 3-Way-Routing und `criterion`-Enum)
  - REQ-19: „If the Critic raises identical concerns in two consecutive cycles, the outer loop aborts" (heute: gilt weiter, aber der Vergleich läuft über `structure/docs/design`-Feedback-Strings gemischt, nicht nur Critic-Prosa)
  - REQ-20: „aborts after `MAX_CRITIC_ITERATIONS` rejections" (Konstante existiert noch, ist aber der Design-Cycle-Ceiling, nicht Critic-Cycles)
  - Sektionstitel „Critic-Actor pattern" wörtlich veraltet — heute Option-H DoD gates
- **Impact.** Das REQ-Doc ist die zitierbare Requirements-Referenz für Code-Kommentare (`REQ-XX` überall im Codebase). Wer REQ-16 oder REQ-17 nachschlägt liest inkonsistente Beschreibung des IST-Verhaltens. Konkret: `prompts.py`, `loops.py`, `test_prompts.py`, `test_loops.py` haben `# REQ-15`, `# REQ-16`, `# REQ-17`, `# REQ-18`, `# REQ-19`, `# REQ-20` Kommentare an Stellen, deren tatsächliches Verhalten von der REQ-Beschreibung abgekommen ist. Wenn wir eines Tages einen Code-Review-Run gegen die REQ-Doc laufen lassen, würde die Diskrepanz Alarm schlagen — richtigerweise.
- **Proposed shape.** Zwei Optionen:
  1. **In-place Rewrite** von REQ-15..REQ-20: Sektion umbenennen in „Solution-quality gates (Option-H DoD)". Jede REQ auf das neue Verhalten aktualisieren. Beispiel für REQ-17: „The final_approval reviewer outputs a JSON verdict `{approve, route_to, criterion, reason}` with `criterion` from a 7-value enum; verdicts are parsed with a design-first bias on any failure." Alte REQ-Nummern behalten damit `# REQ-17` im Code stimmt.
  2. **Append + Supersede**: alte REQ-15..REQ-20 mit „SUPERSEDED — see REQ-42..REQ-4X below" markieren, dann neue REQ-42+ hinzufügen die die neuen Gates beschreiben. Sauberer Trail. Aber macht Code-Kommentare wie `# REQ-17` stale, weil die Code-Stelle jetzt auf REQ-42 sollte.

  Empfehlung: **Option 1**. REQ-Nummern sind stabile Anker im Code — Verhalten kann sich weiterentwickeln, Anker bleibt.

  Extra: neue REQs für die drei Gates selbst hinzufügen (REQ-42 = Struktur-Check, REQ-43 = Docs-Write mit Escape, REQ-44 = Final-Approval mit 3-Way + Cycle-Guardrail) UND ins REQ-Doc reinschreiben dass CLI-Flag `--max-critic-iterations` historischer Name für Design-Cycle-Ceiling ist (siehe [[030-option-h-e2e-followups]] #4 Fix).
- **Source.** Bei der Umbenennung `[critic: N cycle]` → `[design: N cycle]` in Item 030 #4 aufgefallen: `docs/orchestrator-requirements.md` referenziert das alte Verhalten wörtlich. Ironisch: genau die Art Doku-Drift die der Docs-Write Gate (Item 028) verhindern soll — hätte er beim Bau von Option-H schon existiert, wäre die Drift beim Merge aufgefallen.
