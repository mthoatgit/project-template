---
status: template
---

# TEST-<NNNN> — <short title>

> **Template file — structural mode.** Copy to `TEST-<NNNN>-<slug>.md` (next global counter — check `index.md`); fill placeholders; drop this frontmatter + banner; add a row to `index.md`.

**Epic:** <E<N>-<slug> OR none>
**Mode:** structural
**Source:** [[NNN-slug]]
**REQ:** <REQ-ID>[, <REQ-ID>...]
**Task:** <TASK-<NNNN>>[, ...]

## Assertion

<Structural claim in RFC 2119 language — e.g. "Every file under `docs/tasks/` MUST match `^(TASK|BUG)-\d{4}-[a-z0-9-]+\.md$` OR be one of the scaffolding files.">

## Verified by

```sh
<Exact command / script — runnable as-is. Exit 0 = pass; non-zero = fail. State stdout shape if informative.>
```

## Notes

<Optional: exceptions, edge cases, dependencies on other tests. Omit if none.>
