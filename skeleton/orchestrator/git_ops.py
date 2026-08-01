"""Git operations — commit each task (REQ-21), look up completed tasks
(REQ-22), reset the last orchestrator commit (REQ-24), and the resume
check (REQ-23..25)."""
import re
import subprocess
import sys

from . import runner  # runner.run_tests — module-attribute access so
                      # @patch("orchestrator.runner.run_tests") works.
from .config import GIT_COMMIT_PREFIX, MAX_ERROR_CHARS


def _head_commit_subject(project_dir: str) -> str:
    """Return the subject line of HEAD, or empty string on failure."""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--pretty=%s"],
            cwd=project_dir, capture_output=True, text=True, encoding="utf-8",
        )
    except Exception:
        return ""
    return result.stdout.strip() if result.returncode == 0 else ""


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
    ids: list[str] = []
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
    """Remove the last commit with ``git reset --hard HEAD~1``."""
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
    """Determine which tasks remain and whether there is revert context.

    Returns ``(tasks_to_run, revert_context)``. ``revert_context`` is
    non-None only when a previous commit was reset because it caused test
    failures — it is passed to the re-implementation prompt so Claude
    understands why the task is being retried (REQ-24).
    """
    completed_ids = get_completed_task_ids(project_dir)

    if not completed_ids:
        return tasks, None

    print(f"[Resume] {len(completed_ids)} task(s) found in git history")
    print(f"[Resume] Running test suite to verify repository state...")
    passed, test_output = runner.run_tests(test_cmd, project_dir)

    if passed:
        remaining = [t for t in tasks if t["id"] not in completed_ids]
        skipped = len(tasks) - len(remaining)
        print(f"[Resume] Tests green — skipping {skipped} completed task(s), "
              f"{len(remaining)} remaining")
        return remaining, None

    # Tests fail. Before auto-resetting, make sure HEAD really is an
    # orchestrator commit — if the user manually committed on top (revert,
    # fix, docs, ...), we must NOT touch it (REQ-42).
    head_subject = _head_commit_subject(project_dir)
    if not head_subject.startswith(GIT_COMMIT_PREFIX):
        print(
            f"[Resume] Tests failed, but HEAD is not an orchestrator commit:\n"
            f"[Resume]   {head_subject or '<no HEAD>'}\n"
            f"[Resume] A manual commit is on top of the orchestrator history —\n"
            f"[Resume] refusing to auto-reset it. Reconcile the tree yourself\n"
            f"[Resume] (git log / git reset) and rerun.",
            file=sys.stderr,
        )
        sys.exit(1)

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
