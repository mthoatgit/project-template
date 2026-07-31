---
status: template
---

# TEST-<NNNN> — <short title>

> **Template file — behavioral mode.** Copy to `TEST-<NNNN>-<slug>.md`; fill placeholders; drop this frontmatter + banner; add a row to `index.md`.

**Epic:** <E<N>-<slug> OR none>
**Mode:** behavioral
**Layer:** <unit | slice | integration | e2e>
**Source:** [[NNN-slug]]
**REQ:** <REQ-ID>[, ...]
**Task:** <TASK-<NNNN>>[, ...]
**Entry-point:** <yes | no — MUST be yes for at least one behavioral test per user-observable outcome per Epic>

## Given

<Preconditions — narrative.>

## When

<The action / trigger — narrative.>

## Then

<Assertion(s) in RFC 2119 language.>

## Notes

<Optional: fixtures, mocks, dependencies. Omit if none.>
