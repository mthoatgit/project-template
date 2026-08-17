---
status: template
---

# <The question, as a question — one line>

> **Template file.** Copy to `docs/backlog/<NNN>-<slug>.md` (NNN = highest existing ID + 1, zero-padded to 3 digits; slug in kebab-case). Replace the frontmatter above with the spike item frontmatter (`type: spike`, `status: raw`, `created: <today>`, `updated: <today>`, `stage: 1`, `stage_attempt: 1`, plus `serves:` and `timebox:` — see below) and remove this banner. See the `workflow-backlog` skill for structure and `workflow-lifecycle-spike` for how this item's stages work.
>
> **A spike is never started by Claude.** The user starts it. Claude may propose one when a decision visibly hinges on an unvalidated technical assumption, and then waits.

**Lifecycle:** spike — see `workflow-lifecycle-spike`

<!--
Spike frontmatter carries two fields the other types do not:

  serves: [013, 015]        # items waiting on the answer — MUST NOT be empty.
                            # A spike that answers nobody's question has no
                            # reason to run. Entries may name items in another
                            # repository; write those as `repo/NNN`.
  timebox: "one Epic run"   # the agreed limit, in whatever unit actually bounds
                            # this spike — wall-clock, runs, or spend. In
                            # frontmatter rather than prose so a spike that has
                            # outrun it is visible.

Terminal statuses: `done` (the question was answered — a negative answer is an
answer), `inconclusive` (the time-box expired with no answer), `dropped`.
-->

## Question

<Exactly one question. Answerable, and decision-shaping: its answer changes what
some other item does. Two questions are two spikes.

Frozen at capture — never rewritten. If the question changes, that is a
different spike.

State plainly which items are blocked on it and what each of them will do
differently depending on the answer. If nothing changes either way, there is no
spike here.>

<!--
Stage sections are added as the item enters each stage of the spike lifecycle
(Stage 1 Question → Stage 2 Experiment → Stage 3 Report back).
Each stage has ### Discussion (with #### YYYY-MM-DD sub-headers for dated notes)
+ ### Outcome + **Approved:** date. See workflow-lifecycle-spike for specifics.

Stage 1 is not approved until five things are written down:
  - the question (one, answerable)
  - the METHOD — how it will be answered, what is built, what counts as an answer
  - the exclusions — what will explicitly NOT be built, stated as a limit
  - the timebox, in frontmatter
  - serves, in frontmatter, non-empty

The method belongs here rather than in Stage 2 on purpose: it is where a spike
fails before it starts, and fixing it up front leaves Stage 2 as pure execution.

Stage 3 is not complete until BOTH halves are done — the ADR on `main`, and a
dated note in every `serves` item carrying the answer and what it means for that
item specifically. Editing a Related line to say the spike closed does NOT
count; neither does skipping an item because the answer changes nothing for it.
-->

## Artefacts

<Bumped in the same commit as each stage's ### Outcome. Starts as `pending`.>

- **Stage 1 (Question):** pending
- **Stage 2 (Experiment):** pending
- **Stage 3 (Report back):** pending

<!--
Optional. Add when this item cross-references others beyond `serves` — a spike
whose result spawned a new item, or a sibling spike on the same subject.
`serves` entries do not need repeating here.

Remove the header entirely if it stays empty.

## Related
- [[NNN-other-item]] — <one-line reason>
-->
