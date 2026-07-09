# Workflow Backlog

Living list of process and tooling improvements to circle back on.
**Meta-level** — about the workflow itself (skills, orchestrator,
conventions), not about any single project's features or bugs.

Items land here when a session ends with something unfinished or
identified as a gap; items move to **Done** when they land in code
or convention.

## Prioritisation

- **P1** — Do next. Something is currently slipping or broken. Fixing prevents ongoing loss.
- **P2** — Design known, build when convenient. Not urgent.
- **P3** — Nice to have. Low value or exploratory.

## Item shape

Each open item follows the same four-line contract so context survives:

- **Symptom** — what breaks today, concretely
- **Impact** — why it matters (what future work suffers)
- **Proposed shape** — enough sketch to start a session cold
- **Source** — where the concern originated (session date / memory link)

---

## Open

### P1 · Backlog itself needs a structure pass before it grows

- **Symptom.** This backlog was seeded 2026-07-09 with 14 open items in a flat single-file list. No convention yet for how items are added, prioritised, moved to Done, archived, or cross-referenced with the memory system and `docs/tasks/index.md`. Currently ad-hoc.
- **Impact.** If items pile up in a poor structure, reorganising later will be expensive and context gets lost. The backlog is the tool that manages every other open item — getting it wrong compounds. Better to shape it while the file is still small.
- **Proposed shape.** Open. Discussion needed across four question groups — captured here so a cold-read tomorrow picks up where we left off:
  - **Lifecycle.** When do we consult it (session start / planning cycle / on demand)? Who adds items (Claude on user request, or spontaneously)? Who prioritises P1/P2/P3 — my "what's slipping" bias may not match yours. What happens to items that turn out wrong or obsolete: delete, mark superseded, move to a "Discarded" section?
  - **Growth.** Stay as one file, or split by category (orchestrator / skills / tooling / conventions)? At 40+ items how do we keep them findable — plain grep, tags, an index at the top? Does the Done section grow unbounded, or archive after X months / N items? Is the four-line contract per item (Symptom / Impact / Proposed shape / Source) worth the overhead at scale, or should it collapse for low-priority items?
  - **Cross-references.** Backlog vs. memory (`project_orchestrator_open_issues.md`) currently overlaps heavily — what's each one's role, or should they merge? Backlog vs. `docs/tasks/index.md` — when does an item graduate from "concept in backlog" to "task in index"? Does the backlog belong in the project-template (ships to every new project) or does each project need its own project-specific backlog too?
  - **Ritual.** Do we need a triage cadence ("walk the backlog on session start" or "weekly")? How do I make sure Claude in a fresh session actually consults the backlog — memory pointer? Explicit slash command `/backlog`? Do we want commands (`/backlog add`, `/backlog move`, `/backlog done`) or is manual editing enough?
- **Source.** 2026-07-09 session — user flagged the backlog structure itself as an important design point before the file grows. Captured for tomorrow so nothing is lost.

---

### P1 · Root Cause + Fix sections stay empty after bug fix

- **Symptom.** After a Class-A bug runs through the orchestrator, the bug file's `## Root Cause` and `## Fix` sections still read `_To be filled in during handling._`. B01 and B02 shipped this way on 2026-07-09.
- **Impact.** No written trace of *why* the bug existed or *why* the tests missed it. Same class of bug hits again → we relearn from scratch instead of reading history. Directly weakens the workflow's key value proposition.
- **Proposed shape.** New `diagnose_phase` in `orchestrator/loops.py`, between the reproducer step (`write_tests_phase`, verified RED) and the fix step (`ralph_loop`). Claude reads the failing test output + bug file and writes into `## Root Cause` BEFORE any fix. That diagnosis is pinned; Fix prompt receives it as context; Critic evaluates fix quality *against* the written diagnosis. `## Fix` section back-filled with the commit SHA after commit lands (auto).
- **Source.** 2026-07-09 session — user flagged Root Cause as "load-bearing artifact" that current setup doesn't enforce. See also [[project_orchestrator_open_issues]] "Root Cause not enforced".

---

### P1 · Regression scenarios not appended to Epic test docs

- **Symptom.** Claude wrote real test code for B01 and B02 (`b01_root_widget_wired_test.dart`, `test_cross_origin_request_returns_access_control_allow_origin_header`) — but never appended the corresponding S32 / S33 scenario rows to `docs/tests/epics/E3-live-status-view.md`. The test-scenario doc lies about coverage.
- **Impact.** Documentation drift from reality. Someone reading only the E3 test doc sees old coverage; someone reading only the code doesn't know the rationale for the scenario. Same failure class as Root Cause — orchestrator skips artifacts that aren't automatically verifiable.
- **Proposed shape.** Reproducer step (`write_tests_phase` for bugs) must append the scenario row to the Epic test file *before* writing the actual test code, using the same append-only convention as Phase 4. If the append doesn't happen or the target file doesn't exist, the item bails to `action needed`.
- **Source.** 2026-07-09 orchestrator run against B01+B02 — spotted the gap while verifying the fixes.

---

### P1 · workflow-implementation skill is task-only

- **Symptom.** Skill describes tasks, `[start-epic]`, "one commit per task", `/ship-epic` — never mentions bugs, though bugs are now first-class work items in the same index and folder.
- **Impact.** Skill and reality drift. Someone loading only `workflow-implementation` won't know bugs share the same flow, folder, and commit format.
- **Proposed shape.** Update skill: bug commits alongside task commits per Epic, orchestrator processes both types via `docs/tasks/index.md`, `/ship-epic` bundles both, commit format for both is `[orchestrator] <ID> — tests pass, design approved` (feat/fix distinction not yet enforced — see P3 item).
- **Source.** 2026-07-09 session review.

---

### P1 · Manual `fix:` commits bypass the orchestrator bug flow

- **Symptom.** During the 2026-07-09 session, after the folder restructure exposed a five-column-vs-four-column parser mismatch in the dashboard, Claude fixed it as a manual `fix:` commit (`672b879`) instead of filing B03 and routing through the extended orchestrator. The manual path was chosen for speed. The same shortcut will surface every time a defect appears mid-session — quick manual fix always feels faster than filing a bug and starting a subprocess.
- **Impact.** The whole point of the bug-flow discipline (regression test first, Class A/B routing, Ralph + Critic loop, `[orchestrator]` commit format) is *repeatable, documented protection*. Every manual `fix:` bypass teaches Claude "this is the easier path" — over time the orchestrator becomes ceremonial rather than default, and the disciplined pattern erodes. The value we invested in building the bug flow only pays off if the bug flow is what actually runs.
- **Proposed shape.** Convention rule to add (candidate homes: `workflow-implementation` skill, a new `workflow-integrity` note, or the top-level `CLAUDE.md`): **Claude MUST file every observed defect as `B<NN>-*.md` before touching production code, even when the fix is small.** Manual `fix:` commits are reserved for cases where the orchestrator itself is broken (bootstrapping problem). Trade-off: adds ceremony to small fixes; the reason it's worth the cost is that discipline drift silently kills the workflow's value proposition. To reduce the ceremony cost, a fast-path helper — a slash command like `/file-bug <one-liner>` that scaffolds a `B<NN>.md` from in-session context with a template symptom + reproduction — could make filing feel less like paperwork.
- **Source.** 2026-07-09 session — user flagged the parser fix post-hoc as the wrong choice ("das stört mich sehr — nicht am orchestrator vorbeilaufen"). Concrete instance: commit `672b879` should have been B03 → orchestrator instead.

---

### P2 · Task implementation has no explicit planning step

- **Symptom.** The task flow goes straight from reading the task file (Goal + Steps + AC) to `write_tests_phase` to `ralph_loop`. Claude never explicitly forms and pins a plan — "here's what I intend to build, which files I'll touch, which interfaces I'll change" — before starting. The Critic reviews the *result*, not the intended *approach*. Whatever plan existed lives only inside Claude's context and disappears with the subprocess.
- **Impact.** Somewhere between "silently drifts from the task spec" and "picks a symptomatic implementation when a cleaner one exists". Same class of concern as the P1 Root Cause gap for bugs — without a written plan or diagnosis, evaluation is retrospective rather than prescriptive, and there's no artifact to point at when the outcome disagrees with expectation.
- **Proposed shape.** Open — needs a discussion before design. User wants to talk through the concept first and sanity-check whether it even makes sense before we sketch structure. Direction to explore: an explicit planning step for tasks (semantically parallel to the proposed `diagnose_phase` for bugs). Claude reads the task file, writes a short "here's what I'll build, which files, which interfaces" summary, gets it pinned into the task file or a sidecar, then `write_tests_phase` runs. Fix and Critic prompts receive the plan as context. Open questions to work through together: does this belong per task or at a higher lifecycle level (start-epic ceremony); does the plan get committed with the task file or as a working artifact; can Claude revise the plan mid-run and if so what's the trigger.
- **Source.** 2026-07-09 session — user: "bei der implementierung ein wenig die planung fehlt ich würde gern über ein konzept sprechen wie wir das einbauen können und prüfen zusammen mit dir ob die idee überhaupt sinn macht." Semantically parallel to P1 "Root Cause + Fix sections stay empty" — both flag missing pinned-thinking artifacts, one for tasks, one for bugs.

---

### P2 · Diagnose test-infra bugs vs code bugs

- **Symptom.** When the test command errors *before* any assertion runs (Flutter not on PATH, missing dependency, wrong CWD), Ralph feeds the runner error to Claude as if the implementation were broken.
- **Impact.** Token budget wasted on fixes that will never work; the actual problem (environment, missing tool) is hidden behind a code-review-style error message.
- **Proposed shape.** Before treating a failed run as a code failure, detect "no tests ran" / "runner error" signatures (e.g. `command not found`, `FileNotFoundError`, empty test summary) and abort with a distinct exit reason `test infra broken` — clearly separated from `action needed`.
- **Source.** Earlier session, documented in [[project_orchestrator_open_issues]] "Ralph Loop can't tell test-infra bugs from code bugs".

---

### P2 · MAX_CONSECUTIVE_ABORTS cascade guard

- **Symptom.** If K consecutive items hit `action needed`, orchestrator keeps trying the next one. The `workflow-bugs` skill documents this guard; the code doesn't implement it.
- **Impact.** When there's a systemic problem (test infra, wrong reproducer format, wrong fix strategy), the loop wastes tokens instead of surfacing that something's broken at a higher level.
- **Proposed shape.** In `orchestrator/main.py`, track consecutive `action needed` outcomes across items in a single run; when count reaches `MAX_CONSECUTIVE_ABORTS` (default 3), print a clear message ("3 items in a row aborted — systemic problem, stopping") and exit non-zero.
- **Source.** 2026-07-09 discussion; documented in `workflow-bugs` skill "Orchestrator involvement".

---

### P2 · Dirty working tree after abort

- **Symptom.** When Ralph or Critic hit an exit criterion, whatever Claude last wrote stays in the working tree. The next run has to reconcile the leftover changes before it can proceed cleanly.
- **Impact.** Manual clean-up cost on every aborted run. Also confuses `resume_check` if the leftover changes overlap with the next item's scope.
- **Proposed shape.** On abort, either `git stash push -u -m "orchestrator-abort <ID>"` to preserve Claude's work in a labelled stash, or `git checkout HEAD -- <changed>` for a clean rollback. Keep `docs/tasks/index.md`'s `action needed` state — that IS the intended abort signal and must persist.
- **Source.** Earlier session, documented in [[project_orchestrator_open_issues]].

---

### P2 · Structured smoke concept

- **Symptom.** Manual smoke tests are aspirational — S25 in the dashboard's E3 test doc was labelled `Manual / smoke` but never actually ran, and that's precisely what let B01+B02 through. There's no forcing function that gates `done` behind smoke execution.
- **Impact.** Class B bugs (browser rendering, layout, real network under load, UX flow) have no systematic gate before "done" fires. Every Epic risks a repeat of the empty-page-shipped scenario.
- **Proposed shape.** User was designing this — batched, structured smoke at Epic-close (not per task, to avoid mid-flow interruption). Listing what the human must verify before merging. Design not yet complete. Once ready: Epic Acceptance Criteria could carry a `Manually smoke-verified:` bullet that `/ship-epic` refuses to skip.
- **Source.** 2026-07-09 discussion; user explicitly deferred to think it through.

---

### P2 · Logging is prose-mixed, hard to reconstruct retrospectively

- **Symptom.** Orchestrator writes two log files per run — a full log and a filtered progress log — but both are raw prose mixing prompts, Claude subprocess output (long Flutter/pytest test dumps), status markers (`[Ralph Loop]`, `[Fix]`, `[Critic]`, `[OK]`, `[FAIL]`), and errors in one chronological stream. No structured filtering, no per-item organization, no decision-point index, no explicit exit-reason surface. When an item ends `action needed`, the *why* is buried in prose.
- **Impact.** The orchestrator runs asynchronously to the user's attention — background, minutes to hours per run. When it's done, the user has to collaborate with Claude retrospectively to find what went wrong. Today that means scrolling thousands of lines of test output for a magic string that may or may not exist. The primary block on effective post-hoc diagnosis.
- **Proposed shape.** Options to put on the table (probably some combination):
  - **Structured JSONL sidecar** — each decision-worthy event (prompt sent, tests started, iteration N result with fail count, critic verdict, commit produced, exit) as a JSON line; keep the prose log for reading, use JSONL for filtering.
  - **Per-item log tree** — `logs/orchestrator-<timestamp>/<ID>/{prompt.md, tests-1.log, critic.md, decision.txt, ...}`. Filesystem *is* the index; you `cd` to the item that broke.
  - **End-of-run summary** — `-summary.md` per item: outcome, exit reason if aborted, iteration count, deciding failure output, commit SHA. Points into detail logs.
  - **Timestamps on every internal marker** — enables wall-clock reconstruction and correlates with external signals.
  - **Collapse repeated test output** — keep first + last iteration's test dump verbatim, elide the middle with a count marker so 500 identical lines become one.
- **Source.** 2026-07-09 session — user: "der orchestrator läuft getrennt von meiner wahrnehmung und daher brauche ich retrospektiv die möglichkeit zusammen mit dir besser fehler zu finden."

---

### P2 · `docs/tasks/` folder+file layout not yet final

- **Symptom.** Current shape at `docs/tasks/` mixes concerns at the same level: `index.md` (merged work-item index), `_TEMPLATE_TASK.md` + `_TEMPLATE_BUG.md` (blueprints), and the Epic subfolders `E1/`, `E2/`, `E3/` (actual work items). Templates and the index sit as siblings to the folders they template and index.
- **Impact.** Nothing broken today. Concern is longer-term readability and mental model — a first-time reader scans four different concerns (template, template, index, Epic folders × N) in one directory listing. Also the folder name `tasks/` now holds both tasks and bugs, which is defensible but ambiguous.
- **Proposed shape.** Open — needs a discussion before proposing concrete changes. Options worth putting on the table: move templates into a subfolder (`docs/tasks/_templates/`, `docs/.templates/`), move the index up (project root, `docs/index.md`, or somewhere else), rename `docs/tasks/` to reflect that it holds both tasks and bugs, or accept the current layout and simply document the intent more clearly.
- **Source.** 2026-07-09 — user flagged the layout as not final at end of session, wants to revisit deliberately.

---

### P3 · Dashboard doesn't display Type column

- **Symptom.** Merged index has `Type: task | bug`, but the dashboard frontend Task table renders only ID / Epic / Title / Status. Bugs render identically to tasks in the UI.
- **Impact.** Cosmetic; nothing depends on it. Anyone using the dashboard can't visually tell tasks from bugs.
- **Proposed shape.** Thread `type` through the backend `Task` dataclass + `/api/tasks` response, add a column to the `TaskTable` widget. Small feature, one atomic task.
- **Source.** 2026-07-09 session — noted while smoke-testing the app.

---

### P3 · MultiEdit deny rule cosmetic warning

- **Symptom.** Every subprocess Claude call prints: `Permission deny rule "MultiEdit(orchestrator/**)" matches no known tool — check for typos.`
- **Impact.** Cosmetic noise in orchestrator output; masks other warnings.
- **Proposed shape.** Either remove the `MultiEdit(orchestrator/**)` line from `orchestrator/subprocess_settings.json` (since `Edit(...)` + `Write(...)` cover the actual write surface), or find the correct tool name if there is one and use it.
- **Source.** Documented across multiple sessions.

---

### P3 · Conventional-Commit distinction feat / fix for orchestrator commits

- **Symptom.** Task commits and bug commits both use the format `[orchestrator] <ID> — tests pass, design approved`. Nothing in the commit subject distinguishes a feature commit (T<NN>) from a bug commit (B<NN>) besides the ID prefix.
- **Impact.** History readers can't skim `git log` and see "these were bug fixes vs those were features" without decoding the ID prefix. Cross-tooling that consumes Conventional Commits (changelog generators, release tooling) won't classify correctly.
- **Proposed shape.** Optional: `[orchestrator] feat: T<NN> — ...` and `[orchestrator] fix: B<NN> — ...`. Requires updating `git_ops.py::get_completed_task_ids` regex to still find the ID. Trade-off: adds visual noise for a benefit that only matters if we ever consume the log programmatically.
- **Source.** 2026-07-09 discussion.

---

## Done

Items that graduated from Open. Kept as a compact log with a
one-line outcome so we know when a concern was retired and how.

- **2026-07-09** — *Entry-point-anchor test rule* added to `workflow-tests` skill. Validated the same day: B01's root-widget regression test caught what widget-in-isolation tests missed.
- **2026-07-09** — *Bug-flow orchestrator variant* built (`item.py`, `bug_variant.py`, `loops.py` dispatch, Class-A reproducer bail-out, Class-B skip). Two live bug fixes B01 + B02 through the same Ralph + Critic loop as tasks.
- **2026-07-09** — *Merged work-item index* consolidated into `docs/tasks/index.md` (5 columns, Type column). Flat `E<N>/` folders, no more `docs/tasks/epics/` intermediate. Sibling templates `_TEMPLATE_TASK.md` + `_TEMPLATE_BUG.md`.
- **2026-07-09** — *`workflow-bugs` skill* — Class A/B routing, test-first regression, shared status model (`pending` for both types), reproducer bail-out documented, cascade guard documented (build pending).
