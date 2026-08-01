"""Tests for orchestrator.main — CLI lifecycle (REQ-21 commit-per-task,
REQ-34 final verification, REQ-40 default --test-cmd)."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


# ─────────────────────────────────────────────────────────────
#  REQ-21  main() commits after each successfully completed task
# ─────────────────────────────────────────────────────────────

@patch("orchestrator.runner.run_tests")
@patch("orchestrator.git_ops.git_commit_task")
@patch("orchestrator.loops.critic_loop")
@patch("orchestrator.git_ops.resume_check")
@patch("orchestrator.item.load_items")
def test_main_commits_after_each_successful_task(
    mock_load, mock_resume, mock_critic, mock_commit, mock_tests, tmp_path,
):  # REQ-21
    from orchestrator import main
    task_a = {"id": "TASK-0001-alpha", "content": "alpha", "type": "task", "class_": None, "epic": "E1-foundation"}
    task_b = {"id": "TASK-0002-beta",  "content": "beta",  "type": "task", "class_": None, "epic": "E1-foundation"}
    mock_load.return_value = [task_a, task_b]
    mock_resume.return_value = ([task_a, task_b], None)
    mock_critic.return_value = True
    mock_commit.return_value = True
    mock_tests.return_value = (True, "all passed")

    # scripts/test.py stub so the REQ-40 prerequisite check does not exit.
    (tmp_path / "scripts").mkdir(parents=True)
    (tmp_path / "scripts" / "test.py").write_text("", encoding="utf-8")

    with patch("sys.argv", [
        "orchestrator.py", "--tasks", "docs/tasks/",
        "--test-cmd", "pytest",
        "--project-dir", str(tmp_path),
    ]):
        with pytest.raises(SystemExit):
            main()

    assert mock_commit.call_count == 2
    committed_ids = [c[0][0] for c in mock_commit.call_args_list]
    assert "TASK-0001-alpha" in committed_ids
    assert "TASK-0002-beta" in committed_ids


# ─────────────────────────────────────────────────────────────
#  REQ-34  main() runs final verification after all tasks
# ─────────────────────────────────────────────────────────────

@patch("orchestrator.runner.run_tests")
@patch("orchestrator.git_ops.git_commit_task")
@patch("orchestrator.loops.critic_loop")
@patch("orchestrator.git_ops.resume_check")
@patch("orchestrator.item.load_items")
def test_main_runs_final_verification(
    mock_load, mock_resume, mock_critic, mock_commit, mock_tests, tmp_path,
):  # REQ-34
    from orchestrator import main
    task_a = {"id": "TASK-0001-alpha", "content": "alpha", "type": "task", "class_": None, "epic": "E1-foundation"}
    mock_load.return_value = [task_a]
    mock_resume.return_value = ([task_a], None)
    mock_critic.return_value = True
    mock_commit.return_value = True
    mock_tests.return_value = (True, "all passed")

    (tmp_path / "scripts").mkdir(parents=True)
    (tmp_path / "scripts" / "test.py").write_text("", encoding="utf-8")

    with patch("sys.argv", [
        "orchestrator.py", "--tasks", "docs/tasks/",
        "--test-cmd", "pytest",
        "--project-dir", str(tmp_path),
    ]):
        with pytest.raises(SystemExit) as exc_info:
            main()

    assert mock_tests.call_count == 1  # final verification ran
    assert exc_info.value.code == 0


# ─────────────────────────────────────────────────────────────
#  REQ-40  --test-cmd defaults to 'python scripts/test.py'
# ─────────────────────────────────────────────────────────────

def test_default_test_cmd_constant_shape():  # REQ-40
    from orchestrator import DEFAULT_TEST_CMD
    assert DEFAULT_TEST_CMD == "python scripts/test.py"


def test_main_errors_when_default_test_cmd_and_no_scripts_test_py(tmp_path):  # REQ-40
    """Default --test-cmd but no scripts/test.py → exit 1 with an actionable message."""
    (tmp_path / "docs" / "tasks").mkdir(parents=True)
    (tmp_path / "docs" / "tasks" / "TASK-0001-foo.md").write_text(
        "# TASK-0001-foo\n\n**Epic:** E1-foundation\n\nDo stuff.\n", encoding="utf-8"
    )
    # tmp_path does NOT have scripts/test.py.

    from orchestrator import main
    with patch("sys.argv", [
        "orchestrator.py",
        "--tasks", str(tmp_path / "docs" / "tasks"),
        "--project-dir", str(tmp_path),
    ]):
        with patch(
            "orchestrator.git_ops.resume_check",
            return_value=([{"id": "TASK-0001-foo", "content": "x", "type": "task", "class_": None, "epic": "E1-foundation"}], None),
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()
    assert exc_info.value.code == 1


def test_main_accepts_explicit_override_when_no_scripts_test_py(tmp_path):  # REQ-40
    """If --test-cmd is passed explicitly, missing scripts/test.py is fine."""
    (tmp_path / "docs" / "tasks").mkdir(parents=True)
    (tmp_path / "docs" / "tasks" / "TASK-0001-foo.md").write_text(
        "# TASK-0001-foo\n\n**Epic:** E1-foundation\n\nDo stuff.\n", encoding="utf-8"
    )

    from orchestrator import main
    with patch("sys.argv", [
        "orchestrator.py",
        "--tasks", str(tmp_path / "docs" / "tasks"),
        "--test-cmd", "pytest -v",  # explicit override, no scripts/test.py needed
        "--project-dir", str(tmp_path),
    ]):
        # Short-circuit before the run — resume_check reports nothing to do.
        with patch("orchestrator.git_ops.resume_check", return_value=([], None)):
            with pytest.raises(SystemExit) as exc_info:
                main()
    assert exc_info.value.code == 0


# ─────────────────────────────────────────────────────────────
#  TEST-0007 (from item 003) — startup does not fail on Epic-ID extraction
# ─────────────────────────────────────────────────────────────


def test_startup_does_not_bind_test_doc_content_variable():
    """TEST-0007 (source counterpart) — orchestrator.main.py's source MUST NOT
    reference ``test_doc_content`` (the old startup-cached aggregate). Per-task
    discovery now happens inside critic_loop, not once at startup."""
    import orchestrator
    main_py = Path(orchestrator.__file__).parent / "main.py"
    src = main_py.read_text(encoding="utf-8")
    assert "test_doc_content" not in src, (
        "main.py MUST NOT reference test_doc_content — that variable "
        "was the pre-Epic-E5 startup-cached aggregate. Per-task "
        "discovery relocated into loops.critic_loop() per REQ-0008."
    )


def test_tasks_module_no_longer_exposes_find_test_doc():
    """TEST-0007 (structural counterpart) — the retired find_test_doc symbol
    MUST be gone from orchestrator.tasks; find_test_docs_for_task is its
    replacement."""
    from orchestrator import tasks as tasks_mod
    assert not hasattr(tasks_mod, "find_test_doc"), (
        "find_test_doc MUST NOT exist on orchestrator.tasks anymore — "
        "it was retired by Epic E5 in favour of find_test_docs_for_task."
    )
    assert hasattr(tasks_mod, "find_test_docs_for_task"), (
        "find_test_docs_for_task MUST exist as the task-based replacement."
    )
