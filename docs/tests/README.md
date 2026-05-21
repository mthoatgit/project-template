# Test Plan

> **Template file.** Index of the test plan. The plan is split per Epic
> to scale with the project. Drop this block once real content exists.

| File | Content | Epic |
|---|---|---|
| [strategy.md](strategy.md) | Test pyramid, layers, "done" definitions, fixtures, CI | — |
| [epics/E<N>-<slug>.md](epics/E<N>-<slug>.md) | <REQ-IDs> scenarios | E<N> |
| [cross-cutting.md](cross-cutting.md) | Error handling, OpenAPI, other cross-module checks | — |
| [e2e.md](e2e.md) | Full-system happy-path flow | <Epic that owns E2E> |

## Coverage Matrix (Task → Test Type)

| Task | Test types | Notes |
|---|---|---|
| T<NN> | <unit / slice / integration / e2e / none> | <short note> |
| T<NN> | <unit / slice / integration / e2e / none> | <short note> |

## Out of Scope

- <Test category deliberately excluded — e.g. contract tests, perf tests, mutation testing>

---

**Approval:** review each Epic file and the cross-cutting / e2e files
individually. Approval covers the whole plan once all listed files are
signed off.
