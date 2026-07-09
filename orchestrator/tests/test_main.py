"""Tests for orchestrator.main — CLI lifecycle (REQ-21 commit-per-task,
REQ-34 final verification, REQ-40 default --test-cmd)."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


# ─────────────────────────────────────────────────────────────
#  REQ-21  main() commits after each successfully completed task
# ─────────────────────────────────────────────────────────────

@patch("orchestrator.runner.run_tests")
@patch("orchestrator.git_ops.git_commit_task")
@patch("orchestrator.loops.critic_loop")
@patch("orchestrator.git_ops.resume_check")
@patch("orchestrator.tasks.find_test_doc")
@patch("orchestrator.tasks.load_tasks")
def test_main_commits_after_each_successful_task(
    mock_load, mock_find_doc, mock_resume, mock_critic, mock_commit, mock_tests, tmp_path,
):  # REQ-21
    from orchestrator import main
    task_a = {"id": "T01-alpha", "content": "alpha"}
    task_b = {"id": "T02-beta",  "content": "beta"}
    mock_load.return_value = [task_a, task_b]
    mock_doc = MagicMock()
    mock_doc.name = "E1-test.md"
    mock_doc.read_text.return_value = "# Test Design"
    mock_find_doc.return_value = mock_doc
    mock_resume.return_value = ([task_a, task_b], None)
    mock_critic.return_value = True
    mock_commit.return_value = True
    mock_tests.return_value = (True, "all passed")

    with patch("sys.argv", [
        "orchestrator.py", "--tasks", "docs/tasks/epics/E1/",
        "--test-cmd", "pytest",
        "--project-dir", str(tmp_path),
    ]):
        with pytest.raises(SystemExit):
            main()

    assert mock_commit.call_count == 2
    committed_ids = [c[0][0] for c in mock_commit.call_args_list]
    assert "T01-alpha" in committed_ids
    assert "T02-beta"  in committed_ids


# ─────────────────────────────────────────────────────────────
#  REQ-34  main() runs final verification after all tasks
# ─────────────────────────────────────────────────────────────

@patch("orchestrator.runner.run_tests")
@patch("orchestrator.git_ops.git_commit_task")
@patch("orchestrator.loops.critic_loop")
@patch("orchestrator.git_ops.resume_check")
@patch("orchestrator.tasks.find_test_doc")
@patch("orchestrator.tasks.load_tasks")
def test_main_runs_final_verification(
    mock_load, mock_find_doc, mock_resume, mock_critic, mock_commit, mock_tests, tmp_path,
):  # REQ-34
    from orchestrator import main
    task_a = {"id": "T01-alpha", "content": "alpha"}
    mock_load.return_value = [task_a]
    mock_doc = MagicMock()
    mock_doc.name = "E1-test.md"
    mock_doc.read_text.return_value = "# Test Design"
    mock_find_doc.return_value = mock_doc
    mock_resume.return_value = ([task_a], None)
    mock_critic.return_value = True
    mock_commit.return_value = True
    mock_tests.return_value = (True, "all passed")

    with patch("sys.argv", [
        "orchestrator.py", "--tasks", "docs/tasks/epics/E1/",
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


@patch("orchestrator.tasks.find_test_doc")
def test_main_errors_when_default_test_cmd_and_no_scripts_test_py(mock_find, tmp_path):  # REQ-40
    """Default --test-cmd but no scripts/test.py → exit 1 with an actionable message."""
    mock_find.return_value = MagicMock(name="doc.md", read_text=lambda **kw: "not a template")
    (tmp_path / "docs" / "tasks" / "epics" / "E1").mkdir(parents=True)
    (tmp_path / "docs" / "tasks" / "epics" / "E1" / "T01-foo.md").write_text("do stuff", encoding="utf-8")
    # tmp_path does NOT have scripts/test.py

    from orchestrator import main
    with patch("sys.argv", [
        "orchestrator.py",
        "--tasks", str(tmp_path / "docs" / "tasks" / "epics" / "E1"),
        "--project-dir", str(tmp_path),
    ]):
        with patch("orchestrator.git_ops.resume_check", return_value=([{"id": "T01-foo", "content": "x"}], None)):
            with pytest.raises(SystemExit) as exc_info:
                main()
    assert exc_info.value.code == 1


@patch("orchestrator.tasks.find_test_doc")
def test_main_accepts_explicit_override_when_no_scripts_test_py(mock_find, tmp_path):  # REQ-40
    """If --test-cmd is passed explicitly, missing scripts/test.py is fine."""
    mock_find.return_value = MagicMock(name="doc.md", read_text=lambda **kw: "not a template")
    (tmp_path / "docs" / "tasks" / "epics" / "E1").mkdir(parents=True)
    (tmp_path / "docs" / "tasks" / "epics" / "E1" / "T01-foo.md").write_text("do stuff", encoding="utf-8")

    from orchestrator import main
    with patch("sys.argv", [
        "orchestrator.py",
        "--tasks", str(tmp_path / "docs" / "tasks" / "epics" / "E1"),
        "--test-cmd", "pytest -v",  # explicit override, no scripts/test.py needed
        "--project-dir", str(tmp_path),
    ]):
        # Short-circuit before the run — resume_check reports nothing to do.
        with patch("orchestrator.git_ops.resume_check", return_value=([], None)):
            with pytest.raises(SystemExit) as exc_info:
                main()
    assert exc_info.value.code == 0
