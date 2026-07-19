---
type: improvement
---

# P2 · Option-H E2E-Run Follow-ups (Beobachtungen aus dem hello-028 Test)

- **Symptom.** End-to-end Verifikation des in [[028-definition-of-done-for-work-items]] implementierten 4-Phasen-Loops (kleines hello-028 Test-Projekt, T01 greet + T02 farewell mit vorpräpariertem CLAUDE.md-Trap, `--max-critic-iterations 1`, Total 3:06). Beide Tasks passed, alle Gates feuerten in Reihenfolge, JSON-Parsing 4/4 erfolgreich — funktional läuft der Loop. Aber der Run legte eine Reihe von Rauheiten offen die einzeln klein, in Summe störend sind. Docs-Rerun-Pfad blieb ungetestet (Actor war beim Trap gründlich → kein Cycle 2 nötig).
- **Impact.** Ohne Fixes: verrauschte Commits, kaputte Guardrail-Illusion, schlecht observable Docs-Phase, terminologische Drift zwischen Skill und Log. Kritisch: Downstream-Projekte die aus dem Template scaffolden erben all diese Defekte.
- **Proposed shape.** Numerierte Punkte-Liste in Prio-Reihenfolge. Jeder Punkt kann als separates Task/Bug ausgetragen werden oder als Micro-Item hier abgehakt bleiben.

## HIGH — beeinträchtigen Loop-Nutzung oder verstecken Bugs

1. ~~**`logs/` und Root-Log-Files landen in jedem Task-Commit.**~~ **Retracted 2026-07-19.** Ursache war ein Test-Setup-Fehler: mein hello-028 Scratchpad-Projekt hatte eine handgeschriebene minimale `.gitignore` (`__pycache__/`, `*.pyc`, `.pytest_cache/`), die den project-template-Default (`*.log` und andere Standards, siehe `.gitignore` in project-template Root) nicht enthielt. In einem echten Downstream-Projekt (das project-template klont/inheritet) werden `logs/orchestrator-*.log`, `*.progress.log` und `orchestrator-run.log` alle vom `*.log`-Pattern gefangen und landen nicht in Commits. Kein template-Fix nötig. **Adjacente offene Frage**: sollte scaffold beim ersten Epic-Start verifizieren dass `.gitignore` die Minimums enthält? Als eigenes Item filen wenn wir das wollen — hier nur festhalten.

2. ~~**`Write(orchestrator/**)` und `MultiEdit(orchestrator/**)` Deny-Rules sind non-functional.**~~ **Done 2026-07-19.** Beide No-op-Zeilen aus `orchestrator/subprocess_settings.json` entfernt; `Edit(orchestrator/**)` bleibt als einzige Regel und deckt Write+MultiEdit ab (Claude-Codes Permission-Modell). Test `test_subprocess_settings_deny_orchestrator_file_writes` aktualisiert um explizit die Abwesenheit der beiden No-op-Regeln zu asserten — Regression wird durch den Test verhindert. REQ-39 in `docs/orchestrator-requirements.md` mit korrekter Begründung umgeschrieben. Verwandtes Item [[015-multiedit-deny-warning]] als Resolved-Sektion aktualisiert und ins Archive verschoben.

3. ~~**Docs-Write-Phase ist stumm im Progress-Log.**~~ **Done 2026-07-19.** In `loops.py` nach `run_claude` auf dem Happy-Path (docs_status != "design_issue") jetzt konstante Zeile `[OK] docs updated`. Der Escape-Pfad hatte bereits `[ESCAPE] Docs actor: ...`. Content-aware Summary (letzte Actor-Zeile extrahieren) als eigenes Item [[031-docs-write-summary-extraction]] deferred, weil UI-only und noch iterierbar.

## MEDIUM — Terminologie- und UX-Drift

4. ~~**`[critic: N cycle(s)]`-Label in Task-Summary + Stats ist Legacy-Terminologie.**~~ **Done 2026-07-19.** Kaskade abgearbeitet: `_finish`-Param `critic_cycles` → `design_cycles`, stats-Key gleich, Label `[design: N cycle]`, Reason-Strings `"design: max cycles"` / `"design: stuck"`, `[Design Cycle]`-Print-Präfix, Loop-Variable `design_iter`, Summary-Column „Design" in `main.py`. **Nicht umbenannt** (bewusst API-stabil gehalten): `critic_loop` Funktionsname, `--max-critic-iterations` CLI-Flag, `MAX_CRITIC_ITERATIONS` Konstante, `max_critic_iterations` Parameter, lokale `critic_feedback` Variable (das ist der Feedback-Carrier zurück zu Ralph, nicht user-facing). CLI-Help-Text erklärt den historischen Namen kurz. Adjacenter Fund als [[032-orchestrator-requirements-drift]] gefiled — die REQ-15..REQ-20 Beschreibungen im REQ-Doc sind noch Pre-028-Wording.

## LOW — Kosmetisch, aber im Auge behalten

5. ~~**Column-Width-Drift in `docs/tasks/index.md` nach `update_task_status`.**~~ **Done 2026-07-19.** `status.py` self-heilt jetzt: neue Helper `_widen_status_column_header` läuft nach dem Row-Rewrite und widens Header + Separator auf `STATUS_WIDTH+2` (kanonische Zellbreite 15). Widen-only, kürzt nie ab. Zwei neue Tests decken (a) narrow-header → auto-widen und (b) bereits-breite-Header → unverändert ab.

6. ~~**Final-Approval-Reviewer flaggt Status-Flip als „cosmetic nit".**~~ **Done 2026-07-19.** Neue „Out of scope"-Sektion im `build_final_approval_prompt` (task + bug-variant) instruiert den Reviewer explizit: `docs/tasks/index.md` und orchestrator run artifacts (`logs/*.log`, `*.progress.log`, `orchestrator-run.log`) silent ignorieren — nicht in Reason erwähnen, nicht klassifizieren. Test guard-t die Klausel gegen Regression.

## TESTING GAPS — real nicht ausgeübt, nur mock-getestet

7. ~~**Docs-Rerun-Pfad (route_to=docs → Cycle 2) e2e nicht validiert.**~~ **Partial done 2026-07-19.** Nach zwei Anläufen (v1 mit 2 „Hi"-Traps, v2 mit 3) hat der Actor stets Cycle 1 approved — realer Claude ist gründlicher als das Failure-Szenario im Item verlangte. Dritter Anlauf (`hello-028-v3`) mit einem **semantischen Trap** (falsche Verhaltens-Behauptung „Raises ValueError when name is empty" ohne Keyword-Overlap zum neuen Code) hat einen ANDEREN Rerun-Pfad live getriggert: **Guardrail 4 (Actor-Fluchtstiege)**. Docs-Actor entdeckte den semantischen Widerspruch, nahm `design_issue_from_docs_attempt`, Ralph rerannte mit Escape-Feedback im nächsten Design Cycle, dann Final-Approval APPROVE. Runtime 2:58, `[design: 2 cycles]` korrekt. Damit ist der DIESER Rerun-Pfad (Escape → Ralph → wieder Docs → Approve) live-verifiziert. Der reine route_to=docs → docs cycle 2 → approve Pfad ist real weiter ungesehen (Actor zu gründlich um Cycle 1 zu übersehen was Reviewer catcht), aber mock-covered durch vier neue Integration-Tests die Prompt-Struktur pinnen: `test_docs_rerun_prompt_carries_full_review_context`, `test_max_docs_cycles_escalation_gives_ralph_labeled_feedback`, `test_docs_escape_gives_ralph_labeled_feedback`, `test_interleaved_struktur_and_docs_failures_route_correctly`. Wenn der Fall real eintritt, catchen die Tests Regressions in Prompt-Struktur; Live-Verifikation warten wir auf den Naturfall.

8. ~~**`MAX_DOCS_CYCLES`-Escalation (Guardrail 3) e2e nicht validiert.**~~ **Partial done 2026-07-19.** Selbe Situation wie #7: real nicht getriggert weil Actor+Reviewer zu präzise, aber mock-covered inkl. neuem `test_max_docs_cycles_escalation_gives_ralph_labeled_feedback` das explizit prüft dass Ralph nach Escalation ein „docs cycle escalation (...)"-labeled Feedback bekommt, kein rohes criterion. Live-Verifikation gemeinsam mit #7 wenn der Naturfall auftritt.

## INSIGHTS — kein Bug, aber wissenswert

9. **Docs-Write-Output hat keinen expliziten Success-Signal.** Parser default-t bei fehlender JSON zu „ok" — funktioniert im Happy-Path. Wenn wir mal Actor-Behavior präzise messen wollen (hat er tatsächlich Files geändert oder war's ein No-Op?), bräuchten wir einen expliziten Marker im Actor-Output. Für jetzt akzeptabel; interessant falls wir Item [[029-tool-use-for-orchestrator-reviewers]] angehen — Tool-Use würde beide Cases sauber trennen.

10. **JSON-in-Text hat 4/4 Gate-Calls sauber geparst.** Sample size 1, aber positives Signal für Variante A aus 028. Bei größerer Nutzung wird's Failures geben — dann relevant wie robust unser Fallback zu „design"-Default wirklich ist.

- **Source.** E2E-Run 2026-07-19 vormittags gegen `hello-028` im scratchpad. Logs unter `hello-028/logs/orchestrator-2026-07-19-08-30.{log,progress.log}`, Commits `0b2e1fa` (T01) + `e771ebf` (T02). Nutzer-Aussage nach Beobachtungs-Report: „erstelle mal ein backlog item mit allen punkten damit wir es nicht verlieren und dann lass uns oben anfangen" — nach Retraction von #1 wird die Fix-Reihenfolge zu: #2 (deny rules) → #3 (docs-write silence) → #7 (docs-rerun retry) → dann Kleinkram.
