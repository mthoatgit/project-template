---
status: template
---

# TEST-<NNNN> — <short title>

> **Template file — procedural mode.** Copy to `TEST-<NNNN>-<slug>.md`; fill placeholders; drop this frontmatter + banner; add a row to `index.md`.

**Epic:** <E<N>-<slug> OR none>
**Mode:** procedural
**Source:** [[NNN-slug]]
**REQ:** <REQ-ID>[, ...]
**Task:** <TASK-<NNNN> — exactly ONE: the primary task whose Ralph Loop must green this test>
<!-- **Also-covers:** <TASK-<NNNN>[, ...] — OPTIONAL, additional tasks this test exercises as a side effect. Informational only; the orchestrator ignores this field. Remove the header entirely when empty. See workflow-tests "Work-item anchoring". -->
**Last verified:** <YYYY-MM-DD by <who> OR never>

## Steps

1. <Step 1 — concrete action the human takes.>
2. <Step 2.>
3. <...>

## Expected observation

<What the human should see. Formulated as a binary judgement (matches / does not match), not a fuzzy impression.>

## Notes

<Optional: environment prerequisites, screenshots, tolerances. Omit if none.>
