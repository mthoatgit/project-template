# P2 · `status.py` akzeptiert Bug-IDs im Code, aber kein Test schützt den B-Pfad

- **Symptom.** `orchestrator/status.py` akzeptiert seit Item 020 sowohl T- als auch B-präfixierte IDs (Regex `[TB]\d+` in Zeile 22 und 47), aber `orchestrator/tests/test_status.py` exerziert ausschließlich T-IDs (T01, T02, T99). Es gibt keinen Test, der `update_task_status(..., "B01", "done")` gegen das Fixture-`INDEX_SAMPLE` (das eine B01-Zeile enthält) ausführt.
- **Impact.** Silent-Regression-Risiko. Wer künftig `status.py` refactort und den B-Zweig kaputt macht, kriegt keinen roten Test — die Grundlage von Item 020 (Bugs sind first-class im Workflow) wäre still unterwandert. Konkret heute in `orchestrator-dashboard` sichtbar geworden: dort läuft eine stale Kopie von `status.py` (T-only + 4-Spalten-Regex), und beim Orchestrator-Run auf B03 (Commit `5c4e938`) kam die Warnung `[status] cannot extract numeric ID from 'B03-…' — skipping`. Der Sync-Gap zum Downstream-Projekt hätte auffallen können, wenn die Template-Tests den B-Pfad erzwungen hätten.
- **Proposed shape.** Ein bis zwei Testfälle in `test_status.py` ergänzen: `update_task_status(tmp_path, "B01", "done")` (bare) und `update_task_status(tmp_path, "B01-something", "done")` (slug-suffixed) gegen `_make_index(tmp_path)` — die `INDEX_SAMPLE`-Fixture hat bereits eine `| B01 | E1 | bug | Something broke | pending |`-Zeile. Assertion: die B01-Zeile trägt danach `done`, die T01/T02-Zeilen bleiben unverändert. Kein Fixture-Umbau nötig. Bewusst nicht auf `[A-Z]+\d+` verallgemeinern (YAGNI). Der Sync-Gap zu bereits existierenden Downstream-Projekten (heute erlebt bei orchestrator-dashboard) ist eine separate, punktuelle Wartungsarbeit — kein Backlog-Item.
- **Source.** Chat-Session 2026-07-18, B03-Orchestrator-Run in `orchestrator-dashboard`. Verwandt: Item 020 (workflow-bugs Skill, done) — hat B-Support im Code eingeführt, ohne die Test-Suite entsprechend zu erweitern.

## Landed — 2026-07-18

Zwei Tests in `orchestrator/tests/test_status.py` ergänzt:
- `test_update_task_status_flips_bug_status_with_slug` — `update_task_status(..., "B01-something", "done")` schreibt die B01-Zeile, T-Nachbarzeilen bleiben unangetastet, Pipe-Zählung stimmt (6 pro Zeile = 5 Spalten).
- `test_update_task_status_matches_bare_bug_id` — bare `"B01"` ohne Slug-Suffix findet die Zeile ebenfalls.

Beide gehen gegen die bestehende `INDEX_SAMPLE`-Fixture, die schon eine B01-Zeile enthält — kein Fixture-Umbau nötig. Volle Status-Suite jetzt 9 Tests, alle grün. Nicht auf `[A-Z]+\d+` verallgemeinert (YAGNI). Sync-Gap zu `orchestrator-dashboard` (der aktuelle Auslöser) wurde separat gefixt — dort einmalig `orchestrator/status.py` an die Template-Version angeglichen.
