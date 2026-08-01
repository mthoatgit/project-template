# Test Plan

This project uses a three-mode verification model (Behavioral / Structural / Procedural) — see [`strategy.md`](strategy.md) for definitions and mode-selection guidance. Individual tests live as flat files directly under `docs/tests/`, globally numbered as `TEST-<NNNN>-<slug>.md`.

## Files

| File | Content |
|---|---|
| [strategy.md](strategy.md) | Verification-mode definitions, mode-selection rule, behavioral test pyramid, "done" per layer, CI integration |
| [index.md](index.md) | All tests with `Mode / Epic / REQ / Task / Status` columns — the coverage matrix falls out of this table |
| [cross-cutting/](cross-cutting/) | Tests for NFRs and system-wide concerns that do not belong to a single Epic |
| `TEST-<NNNN>-<slug>.md` | Individual test files, one per verification atom, flat under `docs/tests/` |
| `_TEMPLATE_BEHAVIORAL.md` / `_TEMPLATE_STRUCTURAL.md` / `_TEMPLATE_PROCEDURAL.md` | Templates, one per mode |

## Out of Scope

- Performance / load testing (not required at current project scope).
- Contract testing between components (single-service scope).
- Mutation testing.
