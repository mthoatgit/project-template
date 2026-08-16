---
type: change
status: raw
created: 2026-08-16
updated: 2026-08-16
stage: 1
stage_attempt: 1
---

# Codify the prepare-present-confirm interaction style (recommendation-first, visual state)

**Lifecycle:** featurework — see `workflow-lifecycle-featurework`

## Artefacts

- **Stage 1 (Concept):** pending
- **Stage 2 (Requirements + Epic-Birth):** pending
- **Stage 3 (Architecture):** pending
- **Stage 4 (Task-Breakdown):** pending
- **Stage 5 (Tests):** pending

## Core

Filed retrospectively from a live orchestrator-dashboard session (2026-08-16, driving `[[004-realign-with-current-workflow-baseline]]` through its 5-stage featurework lifecycle). The user observed the assistant's interaction style during that session and explicitly asked to preserve it: "I really like the style and want you to check whether it is enforced or why do you do that this way because I want it to keep that way." A brief self-audit surfaced that the style is ~80% already enforced across the AskUserQuestion tool description, `~/.claude/CLAUDE.md` ("Discuss before implement", "Name real trade-offs"), `workflow-backlog` ("Always collaborative. Never silent add.", "Advance the design; don't dump a checklist."), and `workflow-lifecycle-featurework` ("Claude MUST NOT silently write an interpretation into `### Discussion`, even when it seems obvious; the user owns intent"), with ~20% living as consistent assistant judgment (concrete rhythm, visual formatting choices). The style has three separable ingredients that today are only implicit as a bundle:

**1. Recommendation-first Q&A.** When presenting a decision, always name concrete options (2–4), flag the first as `(Recommended)` per AskUserQuestion's tool contract, and give reasons at the same visual level as the options — trade-offs where the recommendation sits, not tucked into small print underneath. Never present options as a neutral survey; always take a position.

**2. Present-before-commit (prepare + preview + confirm).** For anything more substantive than a one-liner, write the proposed changes to disk uncommitted, show the user a concise readable summary of what's on disk, then wait for approval before the commit. This turns "silent apply" into "prepared draft" and gives the user a real inspection surface. Applied at every stage close of the featurework lifecycle in the reference session (item 004 Stages 1–4), never once bundled.

**3. Visual state presentation.** Between the "what happened" and the "what's next" ends of every substantive turn, use readable structure — status tables ("Item X frontmatter | value"), `✅ / 🔴 / 🟡` markers to separate confirmed / broken / borderline, short "Wo wir jetzt stehen"-style boxes summarizing current position, clean separation of *what I already did* (commits, files) versus *what I'm proposing* (chat prose + AskUserQuestion). Not decorative — it lets the user hold the whole state at once instead of reconstructing it from prose.

The item's target is to codify all three as an explicit rule set so the bundle survives across sessions and models, rather than depending on the current assistant's judgment lining up with the current enforced fragments. Concrete forms to weigh in the Stage 1 conversation later: an addition to `~/.claude/CLAUDE.md` under a new "Interaction style" heading versus a new workflow-level rule file versus a targeted amendment to `workflow-backlog`'s "Design conversation principles". Whether the codification lands in this repo (`project-template`), in the dotfiles-claude repo (`~/.claude/CLAUDE.md`), or across both is itself a scoping decision for the later stages.

## Related

- [[004-realign-with-current-workflow-baseline]] — the orchestrator-dashboard item whose session surfaced this observation and drove the request to codify. Cross-project reference: that item lives in orchestrator-dashboard's own backlog, not here. This item does not depend on 004 completing; the two are independent workflows.
