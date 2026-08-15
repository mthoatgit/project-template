# Test Plan

This project uses a three-mode verification model (Behavioral / Structural / Procedural) — see [`strategy.md`](strategy.md) for definitions and mode-selection guidance. Individual tests live as flat files directly under `docs/tests/`, globally numbered as `TEST-<NNNN>-<slug>.md`.

## Files

| File | Content |
|---|---|
| [strategy.md](strategy.md) | Verification-mode definitions, mode-selection rule, behavioral test pyramid, "done" per layer, CI integration |
| [index.md](index.md) | All tests with `Mode / Epic / REQ / Task / Status` columns — the coverage matrix falls out of this table |
| `TEST-<NNNN>-<slug>.md` | Individual test files, one per verification atom, flat under `docs/tests/` |
| `_TEMPLATE_BEHAVIORAL.md` / `_TEMPLATE_STRUCTURAL.md` / `_TEMPLATE_PROCEDURAL.md` | Templates, one per mode |

## Out of Scope

- **Behavioral tests.** Nothing in this repository executes — see [ADR 0001](../adr/0001-tech-stack.md). There is no input-to-output semantics to assert, and no test runner to assert it with.
- **A `cross-cutting/` folder.** No NFR spans Epics yet. The folder and its template are one copy from `skeleton/docs/tests/` away when the first one arrives.
- Performance, contract, and mutation testing.
