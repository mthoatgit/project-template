"""Shared constants and helpers for the orchestrator test suite."""
from __future__ import annotations

from unittest.mock import MagicMock

TASK = {
    "id": "TASK-0001-test",
    "content": "Implement foo",
    "path": "docs/tasks/TASK-0001-test.md",
    "type": "task",
    "class_": None,
    "epic": "E1-foundation",
}

_RESUME_TASKS = [
    {"id": "TASK-0001-alpha", "content": "task alpha"},
    {"id": "TASK-0002-beta",  "content": "task beta"},
]

INDEX_SAMPLE = (
    "# Work Items\n"
    "\n"
    "| ID        | Epic | Type | Title                  | Status        |\n"
    "|-----------|------|------|------------------------|---------------|\n"
    "| TASK-0001 | E1   | task | Build and dependencies | pending       |\n"
    "| TASK-0002 | E1   | task | Docker compose stack   | pending       |\n"
    "| BUG-0003  | E1   | bug  | Something broke        | pending       |\n"
)


def _mock_popen(returncode: int = 0, output: str = "") -> MagicMock:
    """Return a mock subprocess.Popen object whose stdout yields ``output`` line by line."""
    mock = MagicMock()
    mock.stdout = iter(output.splitlines(keepends=True))
    mock.returncode = returncode
    return mock


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
