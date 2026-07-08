#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║              ORCHESTRATOR — RALPH LOOP + CRITIC-ACTOR            ║
╚══════════════════════════════════════════════════════════════════╝

WHAT THIS SCRIPT DOES
─────────────────────
This orchestrator automates TDD-based implementation using Claude Code.
It reads task descriptions (written in Markdown), asks Claude to implement
each task, runs the existing tests, and — if they fail — feeds the error
output back to Claude for a fix attempt. Once tests pass, a second Claude
call acts as an adversarial code reviewer (the Critic) to verify the
solution approach is sound, not just correct. After every successfully
completed task the changes are committed to Git. On restart the orchestrator
resumes from where it left off.

The tests are assumed to already exist before the orchestrator runs.
They are generated from requirements (TDD approach) and are never
modified by the orchestrator or by Claude.


THE RALPH LOOP  (inner loop — correctness)
──────────────
For every task the following cycle runs:

  Iteration 0 — first implementation attempt:
    → Claude receives the task description and writes the code.
    → Tests run. If they pass: hand off to the Critic.
    → If they fail: enter the loop.

  Iteration 1..N — fix attempts:
    → Claude receives the original task description PLUS the test
      output from the previous failed run as context.
    → Claude identifies the root cause and fixes the code.
    → Tests run again. Pass → hand off to Critic. Fail → next iteration.

The number of fix attempts is capped (see MAX_ITERATIONS below).
Smart exit criteria abort the loop early when further attempts
would be pointless (see EXIT CRITERIA below).


THE CRITIC-ACTOR PATTERN  (outer loop — solution quality)
─────────────────────────
After the Ralph Loop gets tests to pass, a second Claude call acts as an
adversarial code reviewer. The Critic evaluates the solution approach —
not correctness (tests handle that) but design quality:

  - Is this the natural, idiomatic solution an experienced developer
    would choose?
  - Are appropriate design patterns used for the context?
  - Does it follow clean code principles at design level: Single
    Responsibility, correct abstraction, no structural DRY violations?
  - Would a senior developer accept this in a PR review — not reluctantly,
    but because the approach is genuinely good?

The Critic is explicitly adversarial: its prompt instructs it to find
problems, not confirm the implementation. It does NOT evaluate formatting,
indentation, naming conventions, or other superficial concerns.

Output: APPROVED (one-line reason) or REJECTED (list of design concerns,
no suggested fixes).

If rejected, the implementer receives the task description and the Critic's
concerns — but NOT the rejected code. This prevents anchoring to the wrong
approach and forces a genuine rethink (REQ-18). The outer loop repeats
until the Critic approves or an exit criterion fires.


GIT INTEGRATION & RESUME
─────────────────────────
After every successfully completed task (tests pass + Critic approves),
the orchestrator stages all changes and commits them:

  [orchestrator] T01-task-name — tests pass, design approved

On restart the orchestrator reads git log to identify completed tasks,
then runs the full test suite once:

  Tests green → skip completed tasks, continue from next uncommitted task.

  Tests red   → the last committed task broke something. The orchestrator
                resets it with git reset --hard HEAD~1 and retries that
                task, passing the failing test output as context so Claude
                understands what went wrong. If tests are still red after
                the retry the orchestrator stops and waits for human input.


EXIT CRITERIA — RALPH LOOP
───────────────────────────
After every failed test run the following checks are evaluated in order.
The first one that triggers stops the loop and marks the task as FAILED.

  1. IDENTICAL OUTPUT      — output unchanged → abort immediately
  2. NO NUMERIC PROGRESS   — same failure count for STUCK_STREAK_THRESHOLD
                             consecutive iterations → abort
  3. REGRESSION            — failure count increased → abort
  4. MAX ITERATIONS        — safety ceiling


EXIT CRITERIA — CRITIC LOOP
────────────────────────────
  5. CRITIC APPROVED       — task complete
  6. SAME CRITIC FEEDBACK  — identical concerns in two consecutive cycles
                             → abort
  7. MAX CRITIC ITERATIONS — safety ceiling


HOW FAILURE COUNTS ARE EXTRACTED
─────────────────────────────────
The function extract_failure_count() uses regex to find the total number
of failed tests in the runner output. Supported formats:

  pytest  →  "3 failed", "2 errors"   (from the summary line)
  Maven   →  "Failures: 3, Errors: 1" (from the test report line)
  Gradle  →  same Maven-style pattern
  Jest    →  "3 failed"               (same pytest-style pattern)

Returns None for unknown formats — the loop degrades gracefully.


TASK FORMAT
───────────
Tasks can be supplied as:
  • A directory of .md files  (e.g. docs/tasks/epics/E1/)
    Files named _TEMPLATE.md are skipped automatically.
  • A single .md file
  • A .json file: list of {"id": "...", "content": "..."} objects
  • A .yaml/.yml file: same structure (requires: pip install pyyaml)


USAGE
─────
  python orchestrator.py --tasks docs/tasks/epics/E1/ \\
                         --test-cmd "mvn test"        \\
                         --project-dir .

  python orchestrator.py --tasks tasks/              \\
                         --test-cmd "pytest"         \\
                         --project-dir ./my-project  \\
                         --filter T03                \\
                         --max-iterations 3          \\
                         --max-critic-iterations 2


PREREQUISITES
─────────────
  - Python 3.10+        install via: winget install Python.Python.3.13
  - Claude Code CLI     install via: npm install -g @anthropic-ai/claude-code
                        must be authenticated: run `claude` once interactively
  - Git                 must be initialised in --project-dir
  - ANTHROPIC_API_KEY   NOT required — the CLI handles authentication
  - Test runner         must be installed and on PATH (mvn, pytest, npm, ...)
  - pyyaml              optional, only for .yaml task files: pip install pyyaml
"""

import argparse
import json
import os
import platform
import re
import subprocess
import sys
import time
from pathlib import Path

# Force UTF-8 + write-through so every print() reaches the log file immediately,
# even when stdout is a pipe (Start-Process, CI, nohup, etc.)
for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace", write_through=True)


class _Tee:
    """Write to primary + any number of secondary streams simultaneously.

    flush() is called after every write() so data reaches all destinations
    immediately regardless of Python's internal buffering (important when
    stdout is a pipe or Start-Process redirection).
    """
    def __init__(self, primary, *secondaries):
        self._primary     = primary
        self._secondaries = secondaries

    def write(self, data):
        self._primary.write(data)
        self._primary.flush()
        for s in self._secondaries:
            s.write(data)

    def flush(self):
        self._primary.flush()
        for s in self._secondaries:
            s.flush()

    def __getattr__(self, name):
        return getattr(self._primary, name)


class _ProgressFilter:
    """Wraps a file and only writes lines that are NOT subprocess output lines.

    Subprocess output is forwarded by run_claude() / run_tests() prefixed with
    '  │ '.  This filter buffers incomplete writes until a newline arrives,
    then silently drops lines starting with that prefix.  Everything else
    (task headers, [OK]/[FAIL] markers, summary table) is written through.

    The result is a compact *.progress.log whose entire content fits in a
    short terminal window or tool output pane.
    """
    def __init__(self, file):
        self._file = file
        self._buf  = ""

    def write(self, data):
        self._buf += data
        while "\n" in self._buf:
            line, self._buf = self._buf.split("\n", 1)
            if not line.startswith("  │"):
                self._file.write(line + "\n")
                self._file.flush()

    def flush(self):
        if self._buf and not self._buf.startswith("  │"):
            self._file.write(self._buf)
            self._buf = ""
        self._file.flush()

    def close(self):
        self.flush()
        self._file.close()

# ─────────────────────────────────────────────────────────────
#  REQUIREMENTS
#
#  This block is the single source of truth for what this script
#  must do. To change behaviour:
#    1. Add, edit, or remove a line here
#    2. Tell Claude: "implement the requirements"
#    3. Claude writes/updates the implementation and tests,
#       then verifies all tests pass
#
#  Each requirement has an ID (REQ-NN). Tests reference these IDs
#  so it is immediately visible which requirements are covered
#  and which are not. Requirements marked [no test] need one added
#  before they can be considered verified.
#
#  Task loading
#  REQ-01  Tasks can be loaded from a directory of .md files;
#          files named _TEMPLATE.md are skipped
#  REQ-02  Tasks can be loaded from a single .md file
#  REQ-03  Tasks can be loaded from a .json file containing a
#          list of {"id": "...", "content": "..."} objects
#  REQ-04  Tasks can be loaded from a .yaml / .yml file
#          (test skipped when pyyaml is not installed)
#
#  Failure count extraction
#  REQ-05  extract_failure_count parses pytest summary lines:
#          "X failed", "X errors", or both combined
#  REQ-06  extract_failure_count parses Maven/Gradle summary lines:
#          "Failures: X, Errors: Y"
#  REQ-07  extract_failure_count returns None for unrecognised
#          formats; callers skip count-based checks gracefully
#
#  Ralph Loop — success paths
#  REQ-08  If tests pass on the first implementation attempt,
#          the task proceeds to Critic review
#  REQ-09  If tests pass after a fix attempt, the task proceeds
#          to Critic review
#
#  Ralph Loop — exit criteria
#  REQ-10  [Criterion 1] If test output is byte-for-byte identical
#          to the previous iteration, the loop aborts immediately
#  REQ-11  [Criterion 2] If the failure count is unchanged for
#          STUCK_STREAK_THRESHOLD consecutive iterations, the loop
#          aborts (catches structural thinking errors that raw
#          output comparison would miss)
#  REQ-12  [Criterion 2] The stuck-streak counter resets whenever
#          the failure count improves
#  REQ-13  [Criterion 3] If the failure count increases compared
#          to the previous iteration, the loop aborts immediately
#  REQ-14  [Criterion 4] The loop aborts after MAX_ITERATIONS fix
#          attempts regardless of whether other criteria fired
#
#  Critic-Actor pattern
#  REQ-15  After tests pass, an adversarial Critic reviews the
#          solution approach (not formatting or naming style)
#  REQ-16  The Critic evaluates: idiomatic approach, appropriate
#          patterns, clean code at design level, no anti-patterns
#  REQ-17  The Critic outputs APPROVED or REJECTED with specific
#          design-level concerns; it does not suggest fixes
#  REQ-18  On rejection, re-implementation receives the task
#          description and Critic feedback but NOT the rejected
#          code, to prevent anchoring to the wrong approach
#  REQ-19  If the Critic raises identical concerns in two
#          consecutive cycles, the outer loop aborts
#  REQ-20  The outer loop aborts after MAX_CRITIC_ITERATIONS
#          rejections regardless of whether criterion 19 fired
#
#  Git integration & resume
#  REQ-21  After each successful task, stage all changes and commit
#          with message: "[orchestrator] {task_id} — tests pass,
#          design approved"
#  REQ-22  On startup, parse git log to identify task IDs that
#          were previously committed by the orchestrator
#  REQ-23  If prior commits exist and tests are green on startup,
#          skip completed tasks and continue from the next one
#  REQ-24  If prior commits exist and tests fail on startup,
#          reset the last orchestrator commit (git reset --hard
#          HEAD~1) and retry that task with the failing test
#          output as context
#  REQ-25  If tests still fail after the retry of the reverted
#          task, stop and report — human intervention required
#
#  Platform
#  REQ-26  On Windows the test command is executed via PowerShell
#          (powershell -NoProfile -Command); on all other platforms
#          via the system shell (shell=True)
#  REQ-27  run_claude passes --dangerously-skip-permissions to the
#          claude CLI so that the workspace trust check does not block
#          non-interactive (subprocess) invocations
#  REQ-28  When claude exits with a session-limit error, run_claude
#          parses the reset time from the message, sleeps until then
#          (+ 2 min buffer), and retries automatically.  If the reset
#          time cannot be parsed, the orchestrator exits with code 2
#          and prints the restart command.
#
#  Test writing phase
#  REQ-29  On startup, extract the Epic ID from the --tasks path and
#          search for docs/tests/epics/<Epic>-*.md in the project dir.
#          Exit with code 1 and an actionable message if the file is
#          not found or contains 'status: template' frontmatter.
#  REQ-30  Before each task's first implementation attempt, call Claude
#          to write real tests based on the task spec and test design
#          doc. The prompt forbids stubs and production code.
#  REQ-31  After test writing, detect uncommitted test files (via git
#          diff + untracked) and build a task-scoped test command.
#          Mark the task as failed if no test files were created.
#  REQ-32  Run the task-scoped tests before implementation to verify
#          they FAIL. Log a WARNING if they unexpectedly pass.
#  REQ-33  The Ralph Loop uses the task-scoped test command, not the
#          full --test-cmd, for correctness checking.
#  REQ-34  After all tasks complete, run the full --test-cmd as final
#          verification and include the result in the summary.
#  REQ-35  'python' / 'python3' at the start of --test-cmd is replaced
#          with sys.executable so Windows App-Execution-Alias stubs
#          (Microsoft Store) never intercept the test run.
#  Task-status file
#  REQ-38  docs/tasks/index.md is the single source of truth for task
#          status. Format: a single aligned Markdown table with columns
#          'ID | Epic | Title | Status', one row per task. As each task
#          runs the orchestrator rewrites its row's Status cell:
#          'pending' → 'in progress' before implementation,
#          → 'done' on success (tests pass + Critic approved),
#          → 'action needed' on any abort (Ralph or Critic).
#          Status values are always padded to STATUS_WIDTH so the table
#          alignment stays intact across writes. On resume+revert the
#          reverted task's row is flipped back to 'in progress' before
#          the retry. When index.md is missing (fresh template, or user
#          removed it) the orchestrator logs a warning and continues —
#          status updates are best-effort.
#
#  REQ-37  A second compact log (*.progress.log) is written alongside the
#          full log. It contains only structural lines — task headers,
#          [OK]/[FAIL] markers, Critic verdicts, and the summary table.
#          Lines prefixed '  │ ' (raw subprocess output) are excluded so
#          the file stays small enough to display in any tool window.
#  REQ-36  All output is written in real time:
#          (a) stdout/stderr are reconfigured with write_through=True at
#              startup so Python's text layer never buffers.
#          (b) _Tee.write() flushes both streams after every write so the
#              log file reflects every print() immediately.
#          (c) run_claude() and run_tests() use Popen + line-by-line
#              reading instead of subprocess.run(capture_output=True),
#              forwarding each line (prefixed '  │ ') as it arrives.
#          (d) PYTHONUNBUFFERED=1 is set in the subprocess env for
#              run_tests() so pytest itself does not buffer.
#          (e) The log file is opened with buffering=1 (line-buffered).
# ─────────────────────────────────────────────────────────────


# ─────────────────────────────────────────────────────────────
#  CONFIGURATION
# ─────────────────────────────────────────────────────────────

# Maximum fix attempts per task in the Ralph Loop.
# 5 is a good ceiling: simple tasks fix in 1–2 rounds, complex ones
# rarely benefit from more. Smart early-exit handles stuck cases
# before this ceiling is reached.
MAX_ITERATIONS = 5

# How many consecutive iterations with the same failure count before
# we consider Claude conceptually stuck and abort.
# 2 means: if round N and round N+1 both show the same number of
# failures, the fix attempts aren't helping.
STUCK_STREAK_THRESHOLD = 2

# Maximum Critic review cycles per task.
# After tests pass, the Critic evaluates the solution approach.
# 3 is appropriate: a good solution usually gets approved in 1–2 rounds;
# more rarely helps when the approach is fundamentally wrong.
MAX_CRITIC_ITERATIONS = 3

# Maximum characters of test output fed back to Claude per iteration.
# Keeps prompts focused; the tail is kept (most recent failures are most useful).
MAX_ERROR_CHARS = 6000

# Prefix used in git commit messages to identify orchestrator commits.
GIT_COMMIT_PREFIX = "[orchestrator]"

# ─────────────────────────────────────────────────────────────


def load_tasks(tasks_path: str) -> list[dict]:
    path = Path(tasks_path)
    tasks = []

    if path.is_dir():
        for f in sorted(path.rglob("*.md")):
            if "_TEMPLATE" not in f.name:
                tasks.append({
                    "id": f.stem,
                    "content": f.read_text(encoding="utf-8"),
                    "path": str(f),
                })
    elif path.suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        tasks = data if isinstance(data, list) else [data]
    elif path.suffix in (".yaml", ".yml"):
        try:
            import yaml
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            tasks = data if isinstance(data, list) else [data]
        except ImportError:
            print("[ERROR] PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
            sys.exit(1)
    else:
        tasks = [{
            "id": path.stem,
            "content": path.read_text(encoding="utf-8"),
            "path": str(path),
        }]

    return tasks


def extract_failure_count(output: str) -> int | None:
    """
    Extract the total number of failing tests from runner output.

    Used by the Ralph Loop to detect whether Claude is making progress
    (fewer failures each round) or is stuck (same count repeating).
    Returns None when the format is not recognised — callers must handle
    this gracefully by skipping count-based checks.
    """
    # pytest: "3 failed", "2 errors" (summary line)
    pytest_fail = re.search(r'\b(\d+)\s+failed\b',  output)
    pytest_err  = re.search(r'\b(\d+)\s+errors?\b', output)
    if pytest_fail or pytest_err:
        return (int(pytest_fail.group(1)) if pytest_fail else 0) + \
               (int(pytest_err.group(1))  if pytest_err  else 0)

    # Maven / Gradle: "Failures: 3, Errors: 1"
    mvn_fail = re.search(r'[Ff]ailures?:\s*(\d+)', output)
    mvn_err  = re.search(r'[Ee]rrors?:\s*(\d+)',   output)
    if mvn_fail or mvn_err:
        return (int(mvn_fail.group(1)) if mvn_fail else 0) + \
               (int(mvn_err.group(1))  if mvn_err  else 0)

    return None


# ─────────────────────────────────────────────────────────────
#  Session-limit handling (REQ-28)
#  Edit parse_reset_time() if Claude changes the message format.
# ─────────────────────────────────────────────────────────────

_SESSION_LIMIT_MARKER = "session limit"
_RESET_PATTERN = re.compile(
    r"resets\s+(\d{1,2}:\d{2}\s*(?:am|pm))\s*\(([^)]+)\)",
    re.IGNORECASE,
)


def parse_reset_time(message: str):
    """Parse 'resets 11:40am (Europe/Berlin)' → datetime, or None.

    Returns an aware datetime when the IANA timezone database is available
    (Linux/Mac or Windows+tzdata).  Falls back to a naive local-time datetime
    when timezone resolution fails — Claude displays times in the user's local
    timezone anyway, so the sleep duration is still accurate.
    """
    from datetime import datetime, timedelta
    match = _RESET_PATTERN.search(message)
    if not match:
        return None
    time_str, tz_name = match.group(1).strip(), match.group(2).strip()

    tz = None
    try:
        from zoneinfo import ZoneInfo
        tz = ZoneInfo(tz_name)
    except Exception:
        try:
            from backports.zoneinfo import ZoneInfo  # type: ignore
            tz = ZoneInfo(tz_name)
        except Exception:
            pass  # no timezone database — fall back to local time

    try:
        if tz is not None:
            now = datetime.now(tz)
            reset = datetime.strptime(time_str.upper(), "%I:%M%p").replace(
                year=now.year, month=now.month, day=now.day, tzinfo=tz
            )
            if reset <= now:
                reset += timedelta(days=1)
        else:
            now = datetime.now()
            reset = datetime.strptime(time_str.upper(), "%I:%M%p").replace(
                year=now.year, month=now.month, day=now.day
            )
            if reset <= now:
                reset += timedelta(days=1)
        return reset
    except Exception:
        return None


def handle_session_limit(message: str) -> None:
    """Sleep until the Claude session limit resets, then return for retry."""
    import time
    from datetime import datetime, timedelta

    reset_hint = next(
        (p.strip() for p in message.split("·") if "resets" in p.lower()),
        "reset time unknown",
    )
    reset_dt = parse_reset_time(message)

    print(f"\n[SESSION LIMIT] Hit usage limit — {reset_hint}")

    if reset_dt is None:
        restart_cmd = " ".join(sys.argv)
        print("  Could not parse reset time — cannot auto-resume.")
        print("  Restart manually after the limit resets:")
        print(f"  {restart_cmd}")
        sys.exit(2)
        return  # guard for tests where sys.exit is mocked

    wake_at = reset_dt + timedelta(minutes=2)
    wait_sec = (wake_at - datetime.now(reset_dt.tzinfo)).total_seconds()
    wait_min = int(wait_sec / 60)

    print(f"  Sleeping {wait_min} min (resuming at {wake_at.strftime('%H:%M')} with 2 min buffer)...")
    time.sleep(max(wait_sec, 0))
    print("[SESSION LIMIT] Woke up — resuming\n")


def run_claude(prompt: str, project_dir: str) -> tuple[int, str]:
    """Call the Claude Code CLI in non-interactive (print) mode.

    Output is streamed line-by-line (prefixed with '  │ ') so the log file
    updates in real time during long Claude calls instead of staying silent
    for several minutes.
    """
    while True:
        proc = subprocess.Popen(
            ["claude", "--dangerously-skip-permissions", "-p", prompt],
            cwd=project_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        lines: list[str] = []
        for raw_line in proc.stdout:
            sys.stdout.write(f"  │ {raw_line}")
            lines.append(raw_line)
        proc.wait()
        output = "".join(lines).strip()
        if proc.returncode != 0 and _SESSION_LIMIT_MARKER in output.lower():
            handle_session_limit(output)
            continue
        return proc.returncode, output


def run_tests(test_cmd: str, project_dir: str) -> tuple[bool, str]:
    """Run the configured test command and return (passed, output).

    On Windows: executed via PowerShell so that PowerShell syntax and
    PATH resolution work as expected (REQ-26).
    On other platforms: executed via the system shell.

    'python' at the start of the command is always replaced with the
    interpreter that is running the orchestrator (sys.executable) so that
    Windows App-Execution-Alias stubs cannot intercept the call (REQ-35).

    PYTHONUNBUFFERED=1 is injected into the subprocess environment so that
    pytest and any Python-based test runner flush their output immediately.
    Output is streamed line-by-line so the log file updates in real time.
    """
    resolved = re.sub(r"^python3?\b", sys.executable.replace("\\", "/"), test_cmd)
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"

    if platform.system() == "Windows":
        cmd = ["powershell", "-NoProfile", "-Command", resolved]
        use_shell = False
    else:
        cmd = resolved
        use_shell = True

    proc = subprocess.Popen(
        cmd,
        shell=use_shell,
        cwd=project_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    lines: list[str] = []
    for raw_line in proc.stdout:
        sys.stdout.write(f"  │ {raw_line}")
        lines.append(raw_line)
    proc.wait()
    output = "".join(lines).strip()
    return proc.returncode == 0, output


# ── Task-status file (REQ-38) ─────────────────────────────────

STATUS_REL_PATH = Path("docs") / "tasks" / "index.md"
_STATUS_VALUES = ("pending", "in progress", "done", "action needed")
STATUS_WIDTH   = max(len(v) for v in _STATUS_VALUES)  # 13 ('action needed')

# A task-row Status cell: everything up to the last '|' before the value,
# then the value itself, then optional trailing padding, then the closing '|'.
# The task ID may be bare ('T01') or slug-suffixed ('T01-foo') in the row.
_STATUS_ROW_RE = re.compile(
    r"(?P<prefix>^\|\s*(?P<id>T\d+)(?:-\S*)?\s*\|[^|\n]*\|[^|\n]*\|\s*)"
    r"(?P<status>pending|in progress|done|action needed)"
    r"\s*(?P<close>\|)",
    re.MULTILINE,
)


def update_task_status(project_dir: str, task_id: str, new_status: str) -> bool:
    """Rewrite the Status cell for ``task_id`` in docs/tasks/index.md.

    Matches the row whose ID cell is exactly the task ID's numeric prefix
    (e.g. 'T01' matches both 'T01' and input 'T01-foo'). Missing file or
    unmatched ID → warn and return False; the orchestrator continues
    regardless (status maintenance is best-effort). The written status
    is padded to STATUS_WIDTH so column alignment survives writes.
    """
    if new_status not in _STATUS_VALUES:
        raise ValueError(f"invalid status {new_status!r}; expected one of {_STATUS_VALUES}")

    path = Path(project_dir) / STATUS_REL_PATH
    if not path.exists():
        print(f"  [status] {STATUS_REL_PATH.as_posix()} not found — skipping status update")
        return False

    m = re.match(r"^(T\d+)", task_id)
    if not m:
        print(f"  [status] cannot extract numeric ID from '{task_id}' — skipping")
        return False
    short_id = m.group(1)

    original = path.read_text(encoding="utf-8")
    padded = new_status.ljust(STATUS_WIDTH)
    matched = False

    def _replace(match: "re.Match[str]") -> str:
        nonlocal matched
        if match.group("id") != short_id:
            return match.group(0)
        matched = True
        return f"{match.group('prefix')}{padded} {match.group('close')}"

    updated = _STATUS_ROW_RE.sub(_replace, original)
    if not matched:
        print(f"  [status] no row for '{short_id}' — skipping status update")
        return False

    if updated != original:
        path.write_text(updated, encoding="utf-8")
    return True


# ── Git operations ────────────────────────────────────────────

def git_commit_task(task_id: str, project_dir: str) -> bool:
    """Stage all changes and commit with a standardised orchestrator message."""
    subprocess.run(["git", "add", "-A"], cwd=project_dir, capture_output=True)
    result = subprocess.run(
        ["git", "commit", "-m",
         f"{GIT_COMMIT_PREFIX} {task_id} — tests pass, design approved"],
        cwd=project_dir,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.returncode == 0


def get_completed_task_ids(project_dir: str) -> list[str]:
    """Return task IDs of all tasks previously committed by the orchestrator."""
    result = subprocess.run(
        ["git", "log", "--oneline", f"--grep={GIT_COMMIT_PREFIX}"],
        cwd=project_dir,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    ids = []
    for line in result.stdout.splitlines():
        m = re.search(rf'{re.escape(GIT_COMMIT_PREFIX)}\s+(\S+)', line)
        if m:
            ids.append(m.group(1))
    return ids


def get_last_orchestrator_task_id(project_dir: str) -> str | None:
    """Return the task ID of the most recent orchestrator commit, or None."""
    result = subprocess.run(
        ["git", "log", "-1", "--oneline", f"--grep={GIT_COMMIT_PREFIX}"],
        cwd=project_dir,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if not result.stdout.strip():
        return None
    m = re.search(rf'{re.escape(GIT_COMMIT_PREFIX)}\s+(\S+)', result.stdout)
    return m.group(1) if m else None


def git_reset_hard(project_dir: str) -> bool:
    """Remove the last commit with git reset --hard HEAD~1."""
    result = subprocess.run(
        ["git", "reset", "--hard", "HEAD~1"],
        cwd=project_dir,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.returncode == 0


def resume_check(
    tasks: list[dict],
    test_cmd: str,
    project_dir: str,
) -> tuple[list[dict], str | None]:
    """
    Determine which tasks remain and whether there is revert context for
    the first task (from a previous commit that broke the test suite).

    Returns (tasks_to_run, revert_context).
    revert_context is non-None only when a previous commit was reset because
    it caused test failures — it is passed to the re-implementation prompt
    so Claude understands why the task is being retried (REQ-24).
    """
    completed_ids = get_completed_task_ids(project_dir)

    if not completed_ids:
        return tasks, None

    print(f"[Resume] {len(completed_ids)} task(s) found in git history")
    print(f"[Resume] Running test suite to verify repository state...")
    passed, test_output = run_tests(test_cmd, project_dir)

    if passed:
        remaining = [t for t in tasks if t["id"] not in completed_ids]
        skipped = len(tasks) - len(remaining)
        print(f"[Resume] Tests green — skipping {skipped} completed task(s), "
              f"{len(remaining)} remaining")
        return remaining, None

    # Tests fail — reset last orchestrator commit and retry with context
    last_id = get_last_orchestrator_task_id(project_dir)
    print(f"[Resume] Tests failed — resetting last commit ('{last_id}')...")
    git_reset_hard(project_dir)

    safe_ids  = [id_ for id_ in completed_ids if id_ != last_id]
    remaining = [t for t in tasks if t["id"] not in safe_ids]

    revert_context = (
        f"A previous implementation of this task was rolled back because it "
        f"caused test failures across the suite:\n\n"
        f"{test_output[-MAX_ERROR_CHARS:]}"
    )

    print(f"[Resume] '{last_id}' will be retried with failure context")
    return remaining, revert_context


# ── Prompt builders ───────────────────────────────────────────

def build_implement_prompt(
    task: dict,
    critic_feedback: str | None = None,
    revert_context: str | None = None,
) -> str:
    """
    Build the implementation prompt for Claude.

    critic_feedback: included when the Critic rejected a previous attempt;
                     the rejected code is deliberately omitted to prevent
                     anchoring to the wrong approach (REQ-18).
    revert_context:  included when a previous commit was rolled back due to
                     test failures; tells Claude what broke (REQ-24).
    Both can be present simultaneously.
    """
    sections = []

    if revert_context:
        sections.append(
            f"## Warning — Previous Implementation Was Rolled Back\n"
            f"{revert_context}\n\n"
            f"Implement this task carefully so it does not break any existing tests."
        )

    if critic_feedback:
        sections.append(
            f"A previous implementation passed all tests but was rejected in "
            f"design review for the following reasons:\n\n"
            f"## Design review concerns:\n{critic_feedback}\n\n"
            f"Rethink the approach from scratch. You may delete and recreate "
            f"existing files. Do not patch or reference the previous implementation."
        )

    if not sections:
        sections.append(
            "Implement the following task exactly as specified.\n"
            "Read the relevant existing files first, then write all necessary code.\n"
            "Do not add features beyond what the task requires."
        )

    sections.append(f"## Task ID: {task['id']}\n\n{task['content']}")
    return "\n\n".join(sections)


def build_fix_prompt(task: dict, errors: str, iteration: int) -> str:
    return f"""The implementation of task '{task['id']}' failed the tests (attempt {iteration}).
Analyze the test output below, identify the root cause, and fix the code.

## Test Failures:
{errors}

## Original Task Specification:
{task['content']}

Fix the implementation so that all tests pass. Do not change the tests themselves.
"""


def build_critic_prompt(task: dict) -> str:
    """
    Build the adversarial design-review prompt for the Critic.

    The Critic's mandate is to find problems, not to confirm the implementation.
    It receives no rationale from the implementer to avoid anchoring bias.
    """
    return f"""You are a senior software engineer conducting an adversarial design review.
Your role is to find fundamental problems with the solution approach — not to confirm it.
Be skeptical. If the approach is wrong, say so clearly.

First, read the implementation files relevant to this task.

## Task that was implemented:
{task['content']}

## Evaluate:
- Is this the natural, idiomatic solution an experienced developer would choose?
- Are appropriate design patterns used for the context (not over- or under-engineered)?
- Does it follow clean code principles at design level: Single Responsibility,
  correct abstraction level, no structural DRY violations?
- Would a senior developer accept this approach in a PR review — not reluctantly,
  but because the approach is genuinely good?
- Does it avoid anti-patterns and solutions that technically work but no
  experienced developer would choose?

## Do NOT evaluate:
- Code formatting, indentation, or whitespace
- Naming style conventions (camelCase vs snake_case etc.)
- Comment style or documentation formatting

## Response format (follow exactly):
If the approach is solid:
  APPROVED — [one-line reason]

If there are fundamental problems:
  REJECTED
  - [specific design concern 1]
  - [specific design concern 2]
  ...

Do not suggest fixes. Only identify what is wrong with the current approach.
"""


def parse_critic_output(output: str) -> tuple[bool, str]:
    """
    Parse the Critic's verdict.

    Returns (approved, weaknesses). weaknesses is empty string when approved.
    Scans all lines so that CLI preamble messages (e.g. Claude's stdin warning)
    before the actual APPROVED/REJECTED verdict do not cause a false rejection.
    """
    for line in output.strip().splitlines():
        if line.strip().upper().startswith("APPROVED"):
            return True, ""
    return False, output.strip()


def format_elapsed(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


# ── Test writing phase ────────────────────────────────────────

def find_test_doc(tasks_path: str, project_dir: str) -> "Path":
    """Find and validate the Epic's test design doc (REQ-29). Exits if missing or template."""
    epic_id = None
    for part in Path(tasks_path).parts:
        if re.match(r"^E\d+", part, re.IGNORECASE):
            epic_id = part
            break

    if not epic_id:
        print(
            f"[ERROR] Cannot determine Epic ID from --tasks path: {tasks_path}\n"
            f"        Expected a path containing an Epic folder, e.g. docs/tasks/epics/E1/",
            file=sys.stderr,
        )
        sys.exit(1)

    test_docs_dir = Path(project_dir) / "docs" / "tests" / "epics"
    matches = sorted(test_docs_dir.glob(f"{epic_id}-*.md"))

    if not matches:
        print(
            f"[ERROR] Test design doc not found: docs/tests/epics/{epic_id}-*.md\n"
            f"        Complete Phase 4 (test design) before running the orchestrator.",
            file=sys.stderr,
        )
        sys.exit(1)

    doc = matches[0]
    content = doc.read_text(encoding="utf-8")
    if "status: template" in content[:300]:
        print(
            f"[ERROR] Test design doc is still a template: {doc.relative_to(project_dir)}\n"
            f"        Complete Phase 4 (test design) before running the orchestrator.",
            file=sys.stderr,
        )
        sys.exit(1)

    return doc


def build_write_tests_prompt(task: dict, test_doc_content: str) -> str:
    return (
        f"Read the task specification and test design document, "
        f"then write the tests for this task.\n\n"
        f"Rules:\n"
        f"- Write real, meaningful tests with concrete assertions\n"
        f"- No stubs, no `assert False`, no `pytest.skip`\n"
        f"- Tests must FAIL because the implementation raises NotImplementedError "
        f"— not because assertions are wrong\n"
        f"- Create a new test file — do not modify any existing test files\n"
        f"- Do not write or modify any production/source code in this step\n\n"
        f"## Task {task['id']}:\n{task['content']}\n\n"
        f"## Test Design Document:\n{test_doc_content}\n\n"
        f"Write only the tests for task {task['id']}. "
        f"After writing, the tests should fail with NotImplementedError."
    )


def detect_task_test_files(project_dir: str) -> list[str]:
    """Return test files added or modified since the last commit (REQ-31)."""
    modified = subprocess.run(
        ["git", "diff", "--name-only"],
        cwd=project_dir, capture_output=True, text=True, encoding="utf-8",
    ).stdout.splitlines()

    untracked = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"],
        cwd=project_dir, capture_output=True, text=True, encoding="utf-8",
    ).stdout.splitlines()

    return [
        f for f in modified + untracked
        if re.search(r"[/\\]test_[^/\\]+\.py$", f)
    ]


def build_task_test_cmd(test_cmd: str, test_files: list[str]) -> str:
    """Replace the test directory in test_cmd with specific test files (REQ-33)."""
    files_str = " ".join(test_files)
    scoped = re.sub(r"\S*\btests[/\\]?\S*", files_str, test_cmd)
    return scoped.strip() if scoped != test_cmd else f"{test_cmd} {files_str}".strip()


def write_tests_phase(
    task: dict,
    test_cmd: str,
    test_doc_content: str,
    project_dir: str,
) -> tuple[str, bool]:
    """Call Claude to write tests, then verify they fail (REQ-30, REQ-31, REQ-32)."""
    print(f"\n[Write Tests] '{task['id']}'")
    prompt = build_write_tests_prompt(task, test_doc_content)
    rc, output = run_claude(prompt, project_dir)
    if rc != 0:
        print(f"  [!] claude exited with code {rc}")

    test_files = detect_task_test_files(project_dir)
    if not test_files:
        print("  [ERROR] No test files were created — aborting task")
        return test_cmd, False

    task_test_cmd = build_task_test_cmd(test_cmd, test_files)
    print(f"  Created: {', '.join(test_files)}")

    print(f"\n[Verify]  {task_test_cmd}")
    passed, verify_output = run_tests(task_test_cmd, project_dir)
    if passed:
        print("  [WARNING] Tests pass before implementation — proceeding anyway")
    else:
        fail_count = extract_failure_count(verify_output)
        count_str = str(fail_count) if fail_count is not None else "?"
        print(f"  [OK] {count_str} test(s) failing as expected")

    return task_test_cmd, True


# ── Loops ─────────────────────────────────────────────────────

def ralph_loop(
    task: dict,
    test_cmd: str,
    project_dir: str,
    max_iterations: int,
    critic_feedback: str | None = None,
    revert_context: str | None = None,
) -> bool:
    """
    Inner correctness loop: implement → test → fix → repeat.

    Iteration 0 asks Claude to implement the task from scratch, optionally
    including Critic feedback (REQ-18) or revert context (REQ-24).
    Iterations 1..N ask Claude to fix the code using the previous test output.
    The loop exits as soon as tests pass or one of the four exit criteria fires.

    Returns True if the task's tests eventually pass, False otherwise.
    """
    errors          = None
    prev_output     = None
    prev_fail_count = None
    stuck_streak    = 0

    for iteration in range(max_iterations + 1):
        if iteration == 0:
            print(f"\n[Implement] '{task['id']}'")
            prompt = build_implement_prompt(task, critic_feedback, revert_context)
        else:
            print(f"\n[Ralph Loop] Fix attempt {iteration}/{max_iterations}")
            prompt = build_fix_prompt(task, errors, iteration)

        rc, claude_output = run_claude(prompt, project_dir)
        if rc != 0:
            print(f"  [!] claude exited with code {rc}")

        print(f"\n[Tests]  {test_cmd}")
        passed, test_output = run_tests(test_cmd, project_dir)

        if passed:
            print(f"  [OK] Tests passed in {iteration + 1} attempt(s)")
            return True

        fail_count = extract_failure_count(test_output)
        count_str  = str(fail_count) if fail_count is not None else "?"
        print(f"  [FAIL] {count_str} failure(s)")

        if iteration == max_iterations:
            print(f"  [STOP] Max iterations ({max_iterations}) reached")
            break

        # ── Exit criterion 1: output unchanged ───────────────────
        if test_output == prev_output:
            print("  [STOP] Output identical to previous iteration — stuck")
            break

        # ── Exit criterion 2: no numeric progress ─────────────────
        if fail_count is not None and fail_count == prev_fail_count:
            stuck_streak += 1
            if stuck_streak >= STUCK_STREAK_THRESHOLD:
                print(f"  [STOP] Failure count stuck at {fail_count} for "
                      f"{stuck_streak + 1} iterations — conceptually stuck")
                break
        else:
            stuck_streak = 0

        # ── Exit criterion 3: regression ──────────────────────────
        if fail_count is not None and prev_fail_count is not None \
                and fail_count > prev_fail_count:
            print(f"  [STOP] Regression — {fail_count} failures (was {prev_fail_count})")
            break

        prev_output     = test_output
        prev_fail_count = fail_count

        errors = test_output[-MAX_ERROR_CHARS:] if len(test_output) > MAX_ERROR_CHARS \
            else test_output
        short = errors[:500].replace("\n", " ")
        print(f"  Errors: {short}{'...' if len(errors) > 500 else ''}")

    return False


def critic_loop(
    task: dict,
    test_cmd: str,
    project_dir: str,
    max_ralph_iterations: int,
    max_critic_iterations: int,
    revert_context: str | None = None,
    test_doc_content: str | None = None,
    task_index: int = 0,
    total_tasks: int = 1,
    stats_out: dict | None = None,
) -> bool:
    """
    Outer loop: correctness via ralph_loop, then design quality via Critic.

    Runs ralph_loop to get tests green, then asks the Critic to evaluate the
    solution approach. If rejected, re-runs ralph_loop with the Critic's
    feedback as context (but without the rejected code). Repeats until the
    Critic approves or an exit criterion fires.

    revert_context is forwarded to the first ralph_loop call only, so Claude
    knows a previous commit was rolled back and why (REQ-24).

    Returns True if tests pass AND Critic approves, False otherwise.
    """
    task_start = time.time()
    print(f"\n{'='*64}")
    print(f"  TASK {task_index}/{total_tasks}: {task['id']}")
    print(f"{'='*64}")

    update_task_status(project_dir, task["id"], "in progress")

    def _finish(passed: bool, critic_cycles: int, reason: str) -> bool:
        secs    = time.time() - task_start
        elapsed = format_elapsed(secs)
        if stats_out is not None:
            stats_out.update({"elapsed": secs, "critic_cycles": critic_cycles, "reason": reason})
        update_task_status(
            project_dir, task["id"], "done" if passed else "action needed",
        )
        symbol = "[✓]" if passed else "[✗]"
        status = "PASSED" if passed else "FAILED"
        cycles = (f"critic: {critic_cycles} cycle{'s' if critic_cycles != 1 else ''}"
                  if critic_cycles else "—")
        print(f"\n  {symbol} {task['id']} — {status}  ({elapsed})  [{cycles}]")
        return passed

    # Write tests once before any implementation attempt (REQ-30)
    task_test_cmd = test_cmd
    if test_doc_content is not None:
        task_test_cmd, ok = write_tests_phase(task, test_cmd, test_doc_content, project_dir)
        if not ok:
            return _finish(False, 0, "no tests written")

    critic_feedback = None
    prev_weaknesses = None

    for critic_iter in range(max_critic_iterations + 1):
        if critic_iter > 0:
            print(f"\n[Critic Loop] Re-implementation cycle "
                  f"{critic_iter}/{max_critic_iterations}")

        passed = ralph_loop(
            task, task_test_cmd, project_dir, max_ralph_iterations,
            critic_feedback,
            revert_context if critic_iter == 0 else None,
        )

        if not passed:
            print("  [STOP] Could not get tests to pass — aborting")
            return _finish(False, critic_iter, "tests failed")

        print(f"\n[Critic] Reviewing solution approach...")
        _, critic_output = run_claude(build_critic_prompt(task), project_dir)
        approved, weaknesses = parse_critic_output(critic_output)

        if approved:
            first_line = critic_output.strip().splitlines()[0] if critic_output.strip() else ""
            print(f"  [OK] {first_line}")
            return _finish(True, critic_iter + 1, "passed")

        print(f"  [REJECT] Design concerns:")
        for line in weaknesses.splitlines()[:6]:
            if line.strip():
                print(f"    {line}")

        if critic_iter == max_critic_iterations:
            print(f"  [STOP] Max critic iterations ({max_critic_iterations}) reached")
            return _finish(False, critic_iter + 1, "critic: max cycles")

        if weaknesses == prev_weaknesses:
            print("  [STOP] Critic repeating identical feedback — conceptually stuck")
            return _finish(False, critic_iter + 1, "critic: stuck")

        prev_weaknesses = weaknesses
        critic_feedback = weaknesses

    return _finish(False, max_critic_iterations + 1, "unknown")


def main():
    parser = argparse.ArgumentParser(
        description="Orchestrator — implement tasks via Claude, verify with tests and Critic, "
                    "commit to Git, resume on restart"
    )
    parser.add_argument(
        "--tasks", required=True,
        help="Tasks source: path to a .md file, .json/.yaml file, or a directory of .md files",
    )
    parser.add_argument(
        "--test-cmd", required=True,
        help="Test command to execute, e.g. 'mvn test', 'pytest', 'npm test'",
    )
    parser.add_argument(
        "--project-dir", default=".",
        help="Project root directory — must be a git repository (default: current directory)",
    )
    parser.add_argument(
        "--max-iterations", type=int, default=MAX_ITERATIONS,
        help=f"Max Ralph Loop retries per task (default: {MAX_ITERATIONS})",
    )
    parser.add_argument(
        "--max-critic-iterations", type=int, default=MAX_CRITIC_ITERATIONS,
        help=f"Max Critic review cycles per task (default: {MAX_CRITIC_ITERATIONS})",
    )
    parser.add_argument(
        "--filter", default=None, dest="task_filter",
        help="Only run tasks whose ID contains this string",
    )
    args = parser.parse_args()

    tasks = load_tasks(args.tasks)
    if args.task_filter:
        tasks = [t for t in tasks if args.task_filter.lower() in t["id"].lower()]

    if not tasks:
        print("[ERROR] No tasks found. Check --tasks path or --filter value.", file=sys.stderr)
        sys.exit(1)

    project_dir = str(Path(args.project_dir).resolve())

    # ── Log files ─────────────────────────────────────────────
    log_dir = Path(project_dir) / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp    = time.strftime("%Y-%m-%d-%H-%M")
    log_path     = log_dir / f"orchestrator-{timestamp}.log"
    progress_path = log_dir / f"orchestrator-{timestamp}.progress.log"

    log_file      = open(log_path,      "w", encoding="utf-8", errors="replace", buffering=1)
    progress_file = open(progress_path, "w", encoding="utf-8", errors="replace", buffering=1)
    progress_filter = _ProgressFilter(progress_file)

    _orig_stdout, _orig_stderr = sys.stdout, sys.stderr
    sys.stdout = _Tee(_orig_stdout, log_file, progress_filter)
    sys.stderr = _Tee(_orig_stderr, log_file)

    log_rel      = str(log_path.relative_to(project_dir))
    progress_rel = str(progress_path.relative_to(project_dir))
    if platform.system() == "Windows":
        log_rel      = log_rel.replace("/", "\\")
        progress_rel = progress_rel.replace("/", "\\")
        watch_cmd    = f"Get-Content {log_rel} -Wait -Tail 50 -Encoding utf8"
    else:
        watch_cmd = f"tail -f {log_rel}"
    print(f"[Log]      {log_rel}")
    print(f"[Progress] {progress_rel}")
    print(f"           Watch: {watch_cmd}\n")

    try:
        _run(args, tasks, project_dir, log_path)
    finally:
        sys.stdout = _orig_stdout
        sys.stderr = _orig_stderr
        log_file.close()
        progress_filter.close()


def _run(args, tasks, project_dir: str, log_path) -> None:
    # ── Prerequisite check (REQ-29) ───────────────────────────
    test_doc = find_test_doc(args.tasks, project_dir)
    test_doc_content = test_doc.read_text(encoding="utf-8")
    print(f"[Check] Test design doc: {test_doc.name} — OK")

    # ── Resume check ─────────────────────────────────────────
    tasks_to_run, revert_context = resume_check(tasks, args.test_cmd, project_dir)

    if not tasks_to_run:
        print("All tasks already completed — nothing to do.")
        sys.exit(0)

    print(f"\nOrchestrator starting")
    print(f"  Tasks              : {len(tasks_to_run)} (of {len(tasks)} total)")
    print(f"  Project dir        : {project_dir}")
    print(f"  Test command       : {args.test_cmd}")
    print(f"  Max loop retries   : {args.max_iterations}")
    print(f"  Max critic cycles  : {args.max_critic_iterations}")

    results   = []
    total_tasks = len(tasks_to_run)

    for i, task in enumerate(tasks_to_run):
        stats: dict = {}
        ok = critic_loop(
            task, args.test_cmd, project_dir,
            args.max_iterations, args.max_critic_iterations,
            revert_context=revert_context if i == 0 else None,
            test_doc_content=test_doc_content,
            task_index=i + 1,
            total_tasks=total_tasks,
            stats_out=stats,
        )

        if ok:
            committed = git_commit_task(task["id"], project_dir)
            if not committed:
                print(f"  [!] Git commit failed for '{task['id']}' — continuing anyway")

        results.append({
            "id":            task["id"],
            "passed":        ok,
            "elapsed":       stats.get("elapsed", 0.0),
            "critic_cycles": stats.get("critic_cycles", 0),
            "reason":        stats.get("reason", "unknown"),
        })

        passed_so_far = sum(1 for r in results if r["passed"])
        failed_so_far = len(results) - passed_so_far
        remaining     = total_tasks - (i + 1)
        print(f"  Progress: {i + 1}/{total_tasks}  |  "
              f"passed: {passed_so_far}  failed: {failed_so_far}"
              + (f"  |  next: {tasks_to_run[i + 1]['id']}" if remaining else ""))

    # ── Final verification (REQ-34) ───────────────────────────
    print(f"\n{'='*64}")
    print("  FINAL VERIFICATION")
    print(f"{'='*64}")
    print(f"\n[Final]  {args.test_cmd}")
    final_passed, final_output = run_tests(args.test_cmd, project_dir)
    if final_passed:
        print("  [OK] Full test suite passed")
    else:
        fail_count = extract_failure_count(final_output)
        count_str  = str(fail_count) if fail_count is not None else "?"
        print(f"  [FAIL] {count_str} failure(s) in full suite")

    # ── Summary table ─────────────────────────────────────────
    col = max((len(r["id"]) for r in results), default=10)
    sep = "─" * (col + 38)
    print(f"\n{'='*64}")
    print("  ORCHESTRATOR SUMMARY")
    print(f"{'='*64}")
    print(f"  {'Task':<{col}}  {'Status':<8}  {'Time':>7}  {'Critic'}")
    print(f"  {sep}")
    total_secs = 0.0
    for r in results:
        status  = "PASSED" if r["passed"] else "FAILED"
        elapsed = format_elapsed(r["elapsed"])
        cycles  = (f"{r['critic_cycles']} cycle{'s' if r['critic_cycles'] != 1 else ''}"
                   if r["critic_cycles"] else f"— ({r['reason']})")
        print(f"  {r['id']:<{col}}  {status:<8}  {elapsed:>7}  {cycles}")
        total_secs += r["elapsed"]
    print(f"  {sep}")
    passed_count = sum(1 for r in results if r["passed"])
    failed_count = len(results) - passed_count
    suite_str    = "PASS" if final_passed else "FAIL"
    print(f"  {passed_count} passed  {failed_count} failed  |  "
          f"Total: {format_elapsed(total_secs)}  |  Suite: {suite_str}")
    print(f"{'='*64}\n")

    sys.exit(0 if failed_count == 0 and final_passed else 1)


if __name__ == "__main__":
    main()
