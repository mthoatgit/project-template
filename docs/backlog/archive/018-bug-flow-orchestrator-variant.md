---
type: improvement
---

# Bug-flow orchestrator variant

## Landed — 2026-07-09

Built as `item.py` (unified parser for T/B), `bug_variant.py` (regression-first prompts), `loops.py` dispatch by item type. Class-A reproducer bail-out (regression test must be RED against unfixed code, otherwise `action needed`); Class-B bugs are skipped with a clear log. Same MAX_ITERATIONS + Critic gates as tasks. Validated end-to-end with two live bug fixes B01 + B02 through the same Ralph + Critic loop.
