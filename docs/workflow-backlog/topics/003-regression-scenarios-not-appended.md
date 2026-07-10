# P1 · Regression scenarios not appended to Epic test docs

- **Symptom.** Claude wrote real test code for B01 and B02 (`b01_root_widget_wired_test.dart`, `test_cross_origin_request_returns_access_control_allow_origin_header`) — but never appended the corresponding S32 / S33 scenario rows to `docs/tests/epics/E3-live-status-view.md`. The test-scenario doc lies about coverage.
- **Impact.** Documentation drift from reality. Someone reading only the E3 test doc sees old coverage; someone reading only the code doesn't know the rationale for the scenario. Same failure class as Root Cause — orchestrator skips artifacts that aren't automatically verifiable.
- **Proposed shape.** Reproducer step (`write_tests_phase` for bugs) must append the scenario row to the Epic test file *before* writing the actual test code, using the same append-only convention as Phase 4. If the append doesn't happen or the target file doesn't exist, the item bails to `action needed`.
- **Source.** 2026-07-09 orchestrator run against B01+B02 — spotted the gap while verifying the fixes.
