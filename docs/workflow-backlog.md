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
