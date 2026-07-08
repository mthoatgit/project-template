# Orchestrator Requirements

Single source of truth for what `orchestrator/` must do. To change behaviour:

1. Add, edit, or remove a line here.
2. Tell Claude: "implement the requirements".
3. Claude writes/updates the implementation and tests, then verifies all tests pass.

Each requirement has an ID (`REQ-NN`). Tests reference these IDs so it is
immediately visible which requirements are covered and which are not.
Requirements marked `[no test]` need one added before they can be considered
verified.

---

## Task loading

- **REQ-01** — Tasks can be loaded from a directory of `.md` files;
  files named `_TEMPLATE.md` are skipped.
- **REQ-02** — Tasks can be loaded from a single `.md` file.
- **REQ-03** — Tasks can be loaded from a `.json` file containing a list
  of `{"id": "...", "content": "..."}` objects.
- **REQ-04** — Tasks can be loaded from a `.yaml` / `.yml` file
  (test skipped when `pyyaml` is not installed).

## Failure count extraction

- **REQ-05** — `extract_failure_count` parses pytest summary lines:
  `"X failed"`, `"X errors"`, or both combined.
- **REQ-06** — `extract_failure_count` parses Maven/Gradle summary lines:
  `"Failures: X, Errors: Y"`.
- **REQ-07** — `extract_failure_count` returns `None` for unrecognised
  formats; callers skip count-based checks gracefully.

## Ralph Loop — success paths

- **REQ-08** — If tests pass on the first implementation attempt,
  the task proceeds to Critic review.
- **REQ-09** — If tests pass after a fix attempt, the task proceeds
  to Critic review.

## Ralph Loop — exit criteria

- **REQ-10** — *[Criterion 1]* If test output is byte-for-byte identical
  to the previous iteration, the loop aborts immediately.
- **REQ-11** — *[Criterion 2]* If the failure count is unchanged for
  `STUCK_STREAK_THRESHOLD` consecutive iterations, the loop aborts
  (catches structural thinking errors that raw output comparison would miss).
- **REQ-12** — *[Criterion 2]* The stuck-streak counter resets whenever
  the failure count improves.
- **REQ-13** — *[Criterion 3]* If the failure count increases compared
  to the previous iteration, the loop aborts immediately.
- **REQ-14** — *[Criterion 4]* The loop aborts after `MAX_ITERATIONS` fix
  attempts regardless of whether other criteria fired.

## Critic-Actor pattern

- **REQ-15** — After tests pass, an adversarial Critic reviews the
  solution approach (not formatting or naming style).
- **REQ-16** — The Critic evaluates: idiomatic approach, appropriate
  patterns, clean code at design level, no anti-patterns.
- **REQ-17** — The Critic outputs `APPROVED` or `REJECTED` with specific
  design-level concerns; it does not suggest fixes.
- **REQ-18** — On rejection, re-implementation receives the task
  description and Critic feedback but **not** the rejected code,
  to prevent anchoring to the wrong approach.
- **REQ-19** — If the Critic raises identical concerns in two
  consecutive cycles, the outer loop aborts.
- **REQ-20** — The outer loop aborts after `MAX_CRITIC_ITERATIONS`
  rejections regardless of whether criterion 19 fired.

## Git integration & resume

- **REQ-21** — After each successful task, stage all changes and commit
  with message: `[orchestrator] {task_id} — tests pass, design approved`.
- **REQ-22** — On startup, parse `git log` to identify task IDs that
  were previously committed by the orchestrator.
- **REQ-23** — If prior commits exist and tests are green on startup,
  skip completed tasks and continue from the next one.
- **REQ-24** — If prior commits exist and tests fail on startup,
  reset the last orchestrator commit (`git reset --hard HEAD~1`) and
  retry that task with the failing test output as context.
- **REQ-25** — If tests still fail after the retry of the reverted
  task, stop and report — human intervention required.

## Platform

- **REQ-26** — On Windows the test command is executed via PowerShell
  (`powershell -NoProfile -Command`); on all other platforms via the
  system shell (`shell=True`).
- **REQ-27** — `run_claude` passes `--dangerously-skip-permissions` to the
  `claude` CLI so that the workspace trust check does not block
  non-interactive (subprocess) invocations.
- **REQ-28** — When `claude` exits with a session-limit error, `run_claude`
  parses the reset time from the message, sleeps until then (+ 2 min buffer),
  and retries automatically. If the reset time cannot be parsed, the
  orchestrator exits with code 2 and prints the restart command.

## Test writing phase

- **REQ-29** — On startup, extract the Epic ID from the `--tasks` path and
  search for `docs/tests/epics/<Epic>-*.md` in the project dir. Exit with
  code 1 and an actionable message if the file is not found or contains
  `status: template` frontmatter.
- **REQ-30** — Before each task's first implementation attempt, call Claude
  to write real tests based on the task spec and test design doc. The prompt
  forbids stubs and production code and is language-neutral (no hardcoded
  Python/pytest vocabulary).
- **REQ-31** — After test writing, detect uncommitted test files (via
  `git diff` + untracked). Detection is language-agnostic: files under a
  `tests?/specs?/__tests__` directory OR whose base name follows a common
  test-file convention (`test_X.<ext>`, `X_test.<ext>`, `XTest.<ext>`,
  `X.test.<ext>`, `X.spec.<ext>`) — pytest, Flutter, Go, Rust, JUnit, NUnit,
  Jest / Jasmine, etc. Mark the task as failed if no such files were created.
- **REQ-32** — Run `--test-cmd` before implementation to verify the newly
  written tests FAIL. Log a WARNING if they unexpectedly pass.
- **REQ-33** — The orchestrator is framework-agnostic: `--test-cmd` is a
  project-owned command that runs *all* tests (of any language). The
  orchestrator does NOT scope tests to specific files. Every project
  generated from this template ships a `scripts/test.py` runner (written by
  `/scaffold` from the tech stack in `system-design.md`) that dispatches to
  the right test tools — pytest, flutter test, mvn, gradle, etc.
- **REQ-34** — After all tasks complete, run the full `--test-cmd` as final
  verification and include the result in the summary.
- **REQ-35** — `python` / `python3` at the start of `--test-cmd` is replaced
  with `sys.executable` so Windows App-Execution-Alias stubs (Microsoft Store)
  never intercept the test run.

## Output & logging

- **REQ-36** — All output is written in real time:
  - `stdout` / `stderr` are reconfigured with `write_through=True` at
    startup so Python's text layer never buffers.
  - `_Tee.write()` flushes both streams after every write so the
    log file reflects every `print()` immediately.
  - `run_claude()` and `run_tests()` use `Popen` + line-by-line
    reading instead of `subprocess.run(capture_output=True)`,
    forwarding each line (prefixed `  │ `) as it arrives.
  - `PYTHONUNBUFFERED=1` is set in the subprocess env for
    `run_tests()` so pytest itself does not buffer.
  - The log file is opened with `buffering=1` (line-buffered).
- **REQ-37** — A second compact log (`*.progress.log`) is written alongside
  the full log. It contains only structural lines — task headers,
  `[OK]` / `[FAIL]` markers, Critic verdicts, and the summary table. Lines
  prefixed `  │ ` (raw subprocess output) are excluded so the file stays
  small enough to display in any tool window.

## Task-status file

- **REQ-38** — `docs/tasks/index.md` is the single source of truth for task
  status. Format: a single aligned Markdown table with columns
  `ID | Epic | Title | Status`, one row per task. As each task runs the
  orchestrator rewrites its row's Status cell: `pending` → `in progress`
  before implementation, → `done` on success (tests pass + Critic approved),
  → `action needed` on any abort (Ralph or Critic). Status values are always
  padded to `STATUS_WIDTH` so the table alignment stays intact across writes.
  On resume+revert the reverted task's row is flipped back to `in progress`
  before the retry. When `index.md` is missing (fresh template, or user
  removed it) the orchestrator logs a warning and continues — status updates
  are best-effort.

## Protected-file guardrail

- **REQ-39** — Claude must never modify anything under `orchestrator/` or
  `test_orchestrator.py`. Two layers of defence:
  1. All code-writing prompts (implement, fix, write tests) carry an
     explicit off-limits notice listing PROTECTED_FILES.
  2. After every `run_claude` call, any modifications to those files in the
     working tree are reverted via `git checkout HEAD -- <file>` and a
     WARNING is printed.

  The Critic prompt is exempt — the Critic returns text only and does not
  write files.

## Default test command

- **REQ-40** — `--test-cmd` defaults to `python scripts/test.py`. If the
  default is in use AND `scripts/test.py` does not exist, the orchestrator
  exits with code 1 and a message pointing at `/scaffold`. Override with an
  explicit `--test-cmd` for projects that don't follow this convention.
