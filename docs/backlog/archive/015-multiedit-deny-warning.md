---
type: improvement
---

# P3 · MultiEdit deny rule cosmetic warning

- **Symptom.** Every subprocess Claude call prints: `Permission deny rule "MultiEdit(orchestrator/**)" matches no known tool — check for typos.`
- **Impact.** Cosmetic noise in orchestrator output; masks other warnings.
- **Proposed shape.** Either remove the `MultiEdit(orchestrator/**)` line from `orchestrator/subprocess_settings.json` (since `Edit(...)` + `Write(...)` cover the actual write surface), or find the correct tool name if there is one and use it.
- **Source.** Documented across multiple sessions.

## Resolved 2026-07-19

E2E-Run des Option-H-Loops in [[030-option-h-e2e-followups]] hat gezeigt: die
Warning ist nicht kosmetisch — Claude CLI gab in jedem Call auch aus:
> `Write(orchestrator/**)` is not matched by file permission checks — only
> Edit(path) rules are. Use Edit(orchestrator/**) instead.

Bedeutet: `Write(...)` und `MultiEdit(...)` waren stille no-ops. Der
Guardrail „`orchestrator/` ist off-limits" wurde nur durch
`Edit(orchestrator/**)` durchgesetzt — was tatsächlich alle file-editing
Tools abdeckt (Claude-Codes Permission-Modell).

**Fix.** Beide No-op-Zeilen aus `orchestrator/subprocess_settings.json`
entfernt. Test `test_subprocess_settings_deny_orchestrator_file_writes`
aktualisiert um explizit die Abwesenheit der beiden Regeln zu asserten,
damit sie nicht regressen. REQ-39 in `docs/orchestrator-requirements.md`
umgeschrieben mit korrekter Begründung.
