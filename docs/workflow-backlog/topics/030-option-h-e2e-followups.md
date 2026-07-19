# P2 · Option-H E2E-Run Follow-ups (Beobachtungen aus dem hello-028 Test)

- **Symptom.** End-to-end Verifikation des in [[028-definition-of-done-for-work-items]] implementierten 4-Phasen-Loops (kleines hello-028 Test-Projekt, T01 greet + T02 farewell mit vorpräpariertem CLAUDE.md-Trap, `--max-critic-iterations 1`, Total 3:06). Beide Tasks passed, alle Gates feuerten in Reihenfolge, JSON-Parsing 4/4 erfolgreich — funktional läuft der Loop. Aber der Run legte eine Reihe von Rauheiten offen die einzeln klein, in Summe störend sind. Docs-Rerun-Pfad blieb ungetestet (Actor war beim Trap gründlich → kein Cycle 2 nötig).
- **Impact.** Ohne Fixes: verrauschte Commits, kaputte Guardrail-Illusion, schlecht observable Docs-Phase, terminologische Drift zwischen Skill und Log. Kritisch: Downstream-Projekte die aus dem Template scaffolden erben all diese Defekte.
- **Proposed shape.** Numerierte Punkte-Liste in Prio-Reihenfolge. Jeder Punkt kann als separates Task/Bug ausgetragen werden oder als Micro-Item hier abgehakt bleiben.

## HIGH — beeinträchtigen Loop-Nutzung oder verstecken Bugs

1. ~~**`logs/` und Root-Log-Files landen in jedem Task-Commit.**~~ **Retracted 2026-07-19.** Ursache war ein Test-Setup-Fehler: mein hello-028 Scratchpad-Projekt hatte eine handgeschriebene minimale `.gitignore` (`__pycache__/`, `*.pyc`, `.pytest_cache/`), die den project-template-Default (`*.log` und andere Standards, siehe `.gitignore` in project-template Root) nicht enthielt. In einem echten Downstream-Projekt (das project-template klont/inheritet) werden `logs/orchestrator-*.log`, `*.progress.log` und `orchestrator-run.log` alle vom `*.log`-Pattern gefangen und landen nicht in Commits. Kein template-Fix nötig. **Adjacente offene Frage**: sollte scaffold beim ersten Epic-Start verifizieren dass `.gitignore` die Minimums enthält? Als eigenes Item filen wenn wir das wollen — hier nur festhalten.

2. **`Write(orchestrator/**)` und `MultiEdit(orchestrator/**)` Deny-Rules sind non-functional.** Claude CLI meldet bei jedem Aufruf:
   > `Write(orchestrator/**)` is not matched by file permission checks — only Edit(path) rules are. Use Edit(orchestrator/**) instead (Edit rules cover all file-editing tools).

   Bedeutet: der Guardrail „Claude darf `orchestrator/` nicht schreiben" (REQ-39/41) wird **faktisch nicht durchgesetzt** — nur `Edit(orchestrator/**)` würde alle file-editing Tools abdecken. Fix: `subprocess_settings.json` von `Write(...)`/`MultiEdit(...)` auf `Edit(...)` migrieren. **Verwandt: [[015-multiedit-deny-warning]]** — dort als „cosmetic" markiert, ist es tatsächlich ein kaputter Guardrail. 015 upgraden auf P1.

3. **Docs-Write-Phase ist stumm im Progress-Log.** Zeile 32/58 des progress.log: `[Docs-Write] Cycle 1/2` — kein `[OK]`, kein `[DONE]`, keine Zusammenfassung. Man sieht nur später über die Prosa des Final-Approval Reviewers was der Actor tatsächlich gemacht hat. Fix: analog zu Struktur-Check einen `[OK] <one-liner>` nach `run_claude` in der Docs-Phase printen — auch wenn keine JSON zurückkommt (extrahiere erste sinnvolle Zeile aus der Actor-Ausgabe, oder „docs updated"/„no changes needed" heuristisch).

## MEDIUM — Terminologie- und UX-Drift

4. **`[critic: N cycle(s)]`-Label in Task-Summary + Stats ist Legacy-Terminologie.** Es gibt keinen einzelnen „Critic" mehr, sondern drei Gates. Fix: `[design: N cycle(s)]` in `loops.py::_finish`. Betrifft auch `stats_out["critic_cycles"]`-Key — Umbenennung propagiert durch dashboard/summary. Kleine Kaskade.

## LOW — Kosmetisch, aber im Auge behalten

5. **Column-Width-Drift in `docs/tasks/index.md` nach `update_task_status`.** Status-Cell wird auf `STATUS_WIDTH=13` gepadded, aber Header/Separator werden nicht mitverbreitet. Table rendert als Markdown ok, roh unschön:
   ```
   |-----|------|------|----------|---------|
   | T01 | E1   | task | greet    | done          |
   ```
   Fix: entweder Header beim Erzeugen breit genug erstellen (min 13), oder `update_task_status` re-formatiert die ganze Tabelle auf Max-Width.

6. **Final-Approval-Reviewer flaggt Status-Flip als „cosmetic nit".** Zitat aus T01-Run: „`docs/tasks/index.md` status was bumped to 'in progress' (not a mandatory doc, so out of scope; minor/cosmetic, worth a nit but not blocking)." Reviewer ist etwas übereifrig — kein Bug im Sinne von falschem Verdict, aber Signal dass er Bookkeeping-Änderungen anschaut. Falls Mandatory-Liste eines Tages per-Task konfigurierbar wird, `docs/tasks/index.md` explizit als „ignore this in review" markieren.

## TESTING GAPS — real nicht ausgeübt, nur mock-getestet

7. **Docs-Rerun-Pfad (route_to=docs → Cycle 2) e2e nicht validiert.** Der Trap in hello-028 war zu grob — Actor fixte ihn in Cycle 1. Für erneuten Test-Run brauchen wir einen subtileren Konflikt, den Actor eher übersieht: z.B. eine falsche Signatur oder falscher Return-Wert eines nicht direkt geänderten Beispiels tief in einer README-Sektion, den erst Final-Approval durch Vergleich mit git diff catcht. Nächste E2E-Runde nach den Fixes oben.

8. **`MAX_DOCS_CYCLES`-Escalation (Guardrail 3) e2e nicht validiert.** Weil #7 nicht triggerte, kam Cycle 2 nie zum Einsatz, geschweige denn die Force-to-Design-Route nach Cycle 2. Nur mock-getestet. Selber Test-Design wie #7, aber mit einer Kontradiktion die der Actor auch beim zweiten Anlauf mit Feedback nicht sauber auflösen kann.

## INSIGHTS — kein Bug, aber wissenswert

9. **Docs-Write-Output hat keinen expliziten Success-Signal.** Parser default-t bei fehlender JSON zu „ok" — funktioniert im Happy-Path. Wenn wir mal Actor-Behavior präzise messen wollen (hat er tatsächlich Files geändert oder war's ein No-Op?), bräuchten wir einen expliziten Marker im Actor-Output. Für jetzt akzeptabel; interessant falls wir Item [[029-tool-use-for-orchestrator-reviewers]] angehen — Tool-Use würde beide Cases sauber trennen.

10. **JSON-in-Text hat 4/4 Gate-Calls sauber geparst.** Sample size 1, aber positives Signal für Variante A aus 028. Bei größerer Nutzung wird's Failures geben — dann relevant wie robust unser Fallback zu „design"-Default wirklich ist.

- **Source.** E2E-Run 2026-07-19 vormittags gegen `hello-028` im scratchpad. Logs unter `hello-028/logs/orchestrator-2026-07-19-08-30.{log,progress.log}`, Commits `0b2e1fa` (T01) + `e771ebf` (T02). Nutzer-Aussage nach Beobachtungs-Report: „erstelle mal ein backlog item mit allen punkten damit wir es nicht verlieren und dann lass uns oben anfangen" — nach Retraction von #1 wird die Fix-Reihenfolge zu: #2 (deny rules) → #3 (docs-write silence) → #7 (docs-rerun retry) → dann Kleinkram.
