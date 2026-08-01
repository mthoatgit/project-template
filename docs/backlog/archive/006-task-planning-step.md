---
type: improvement
status: dropped
---

# P2 · Task implementation has no explicit planning step

- **Symptom.** The task flow goes straight from reading the task file (Goal + Steps + AC) to `write_tests_phase` to `ralph_loop`. Claude never explicitly forms and pins a plan — "here's what I intend to build, which files I'll touch, which interfaces I'll change" — before starting. The Critic reviews the *result*, not the intended *approach*. Whatever plan existed lives only inside Claude's context and disappears with the subprocess.
- **Impact.** Somewhere between "silently drifts from the task spec" and "picks a symptomatic implementation when a cleaner one exists". Same class of concern as item 002 (Root Cause gap for bugs) — without a written plan or diagnosis, evaluation is retrospective rather than prescriptive, and there's no artifact to point at when the outcome disagrees with expectation.
- **Proposed shape.** Open — needs a discussion before design. User wants to talk through the concept first and sanity-check whether it even makes sense before we sketch structure. Direction to explore: an explicit planning step for tasks (semantically parallel to the proposed `diagnose_phase` for bugs). Claude reads the task file, writes a short "here's what I'll build, which files, which interfaces" summary, gets it pinned into the task file or a sidecar, then `write_tests_phase` runs. Fix and Critic prompts receive the plan as context. Open questions to work through together: does this belong per task or at a higher lifecycle level (start-epic ceremony); does the plan get committed with the task file or as a working artifact; can Claude revise the plan mid-run and if so what's the trigger.
- **Source.** 2026-07-09 session — user: "bei der implementierung ein wenig die planung fehlt ich würde gern über ein konzept sprechen wie wir das einbauen können und prüfen zusammen mit dir ob die idee überhaupt sinn macht." Semantically parallel to item 002 — both flag missing pinned-thinking artifacts, one for tasks, one for bugs.

## Dropped

**Dropped 2026-08-01.** Reason: backlog reset after the skeleton/ restructure (034) — not evaluated individually.
