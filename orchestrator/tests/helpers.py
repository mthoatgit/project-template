"""Shared constants and helpers for the orchestrator test suite."""
from __future__ import annotations

import subprocess as _real_subprocess
from unittest.mock import MagicMock

TASK = {"id": "T01-test", "content": "Implement foo", "path": "tasks/T01.md"}

_RESUME_TASKS = [
    {"id": "T01-alpha", "content": "task alpha"},
    {"id": "T02-beta",  "content": "task beta"},
]

INDEX_SAMPLE = (
    "# Task Status\n"
    "\n"
    "| ID  | Epic | Title                  | Status        |\n"
    "|-----|------|------------------------|---------------|\n"
    "| T01 | E1   | Build and dependencies | pending       |\n"
    "| T02 | E1   | Docker compose stack   | pending       |\n"
)


def _mock_popen(returncode: int = 0, output: str = "") -> MagicMock:
    """Return a mock subprocess.Popen object whose stdout yields ``output`` line by line."""
    mock = MagicMock()
    mock.stdout = iter(output.splitlines(keepends=True))
    mock.returncode = returncode
    return mock


def _git(cwd, *args):
    """Run a git command in ``cwd`` with a deterministic identity."""
    return _real_subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@t", *args],
        cwd=cwd, capture_output=True, text=True, check=True,
    )


def _make_git_repo(tmp_path, initial_files: dict) -> None:
    """Init a real git repo in ``tmp_path`` with the given files committed."""
    _git(tmp_path, "init", "-q")
    for name, content in initial_files.items():
        (tmp_path / name).write_text(content, encoding="utf-8")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "seed")


def _make_index(tmp_path, body: str = INDEX_SAMPLE):
    """Create a docs/tasks/index.md at tmp_path with the given body and return its path."""
    (tmp_path / "docs" / "tasks").mkdir(parents=True)
    f = tmp_path / "docs" / "tasks" / "index.md"
    f.write_text(body, encoding="utf-8")
    return f


def _row_for(path, task_id: str) -> str | None:
    """Return the first line of ``path`` that starts with the task row for ``task_id``."""
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith(f"| {task_id} "):
            return line
    return None


def task_content_present(prompt: str) -> bool:
    return TASK["content"] in prompt
