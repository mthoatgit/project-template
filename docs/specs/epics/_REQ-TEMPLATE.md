---
status: template
---

# REQ-<NNNN> — <one-line title>

> **Template.** Canonical structure for per-REQ files in
> `docs/specs/epics/E<N>-<slug>/`. To create a new REQ file:
>
> 1. Copy this file into the Epic folder as `REQ-<NNNN>-<slug>.md`
>    (NNNN = next free four-digit global counter across all REQ files
>    in `docs/specs/epics/*/`; slug = topical keyword from the REQ)
> 2. Fill in the header block + requirement text + `## Acceptance`
> 3. Remove this banner and the YAML frontmatter
> 4. Add an index entry in the Epic overview file's
>    `## Functional Requirements` section pointing at this file
> 5. Commit

**Epic:** E<N>-<slug>
**Status:** active
**Source:** [[NNN-slug]]
**Architecture-impact:** pending (see Stage 3)     <!-- or `none (no ADR)`, or `ADR-<NNNN> (<one-line reminder>)` after Stage 3 back-fill -->

<Full requirement text — one or more paragraphs in RFC 2119 normative
style (MUST / SHOULD / MAY). Preserve load-bearing raw language from
the source backlog item verbatim where it tips the meaning.>

## Acceptance

<Observable behavior that proves this requirement. Same abstraction
level as the requirement itself — product framing OK, tech stack NOT.
This is the Business-Analyst-level acceptance; task-level and test-
plan acceptance are added in later phases.>

<!-- Optional -->

## Rationale

<Why this REQ exists / what constraint or discussion produced it.
Optional. Remove if empty.>

## Related

<Other REQs, backlog items, or artefacts that constrain or are
constrained by this one. Optional. Remove if empty.>

- [[REQ-NNNN]] — <reason>
- [[NNN-other-item]] — <reason>

<!--
Supersession — if this REQ is later superseded by another:
- Flip **Status:** from `active` to `superseded`
- Add **Superseded by:** REQ-<NNNN> header line (right below Status)
- Do NOT edit the requirement text or the Acceptance — those are the historical record.
-->
