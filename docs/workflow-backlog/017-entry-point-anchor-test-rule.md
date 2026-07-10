# Entry-point-anchor test rule

## Landed — 2026-07-09

Added to `workflow-tests` skill. For every user-observable outcome, at least one test scenario must anchor at the production entry point (root widget / real HTTP with external `Origin` / `main()`). Widget-in-isolation is allowed only in addition. Validated same day: B01's root-widget regression test caught what widget-in-isolation tests missed.
