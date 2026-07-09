"""Tests for orchestrator.git_ops — commit / resume / reset / task-id lookup
(REQ-21..25)."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

from orchestrator import (
    GIT_COMMIT_PREFIX,
    get_completed_task_ids,
    get_last_orchestrator_task_id,
    git_commit_task,
    git_reset_hard,
    resume_check,
)

from orchestrator.tests.helpers import _RESUME_TASKS


# ─────────────────────────────────────────────────────────────
#  REQ-21  git_commit_task: stage all changes and commit
# ─────────────────────────────────────────────────────────────

@patch("orchestrator.subprocess.run")
def test_git_commit_task_stages_and_commits(mock_run):  # REQ-21
    mock_run.side_effect = [
        MagicMock(returncode=0),                                          # git add -A
        MagicMock(returncode=0, stdout="1 file changed", stderr=""),      # git commit
    ]

    result = git_commit_task("T01-foo", "/project")

    assert result is True
    assert mock_run.call_count == 2
    add_cmd = mock_run.call_args_list[0][0][0]
    assert add_cmd == ["git", "add", "-A"]
    commit_cmd = mock_run.call_args_list[1][0][0]
    assert commit_cmd[:2] == ["git", "commit"]
    commit_msg = commit_cmd[3]
    assert "T01-foo" in commit_msg
    assert GIT_COMMIT_PREFIX in commit_msg


@patch("orchestrator.subprocess.run")
def test_git_commit_task_returns_false_on_git_failure(mock_run):  # REQ-21
    mock_run.side_effect = [
        MagicMock(returncode=0),                                          # git add -A
        MagicMock(returncode=1, stdout="", stderr="nothing to commit"),   # git commit fails
    ]

    result = git_commit_task("T01-foo", "/project")

    assert result is False


# ─────────────────────────────────────────────────────────────
#  REQ-22  get_completed_task_ids: parse git log for orchestrator commits
# ─────────────────────────────────────────────────────────────

@patch("orchestrator.subprocess.run")
def test_get_completed_task_ids_parses_log(mock_run):  # REQ-22
    mock_run.return_value = MagicMock(returncode=0, stdout=(
        "abc1234 [orchestrator] T01-alpha — tests pass, design approved\n"
        "def5678 [orchestrator] T02-beta — tests pass, design approved\n"
    ))

    ids = get_completed_task_ids("/project")

    assert ids == ["T01-alpha", "T02-beta"]


@patch("orchestrator.subprocess.run")
def test_get_completed_task_ids_empty_when_no_prior_commits(mock_run):  # REQ-22
    mock_run.return_value = MagicMock(returncode=0, stdout="")

    ids = get_completed_task_ids("/project")

    assert ids == []


# ─────────────────────────────────────────────────────────────
#  REQ-22  get_last_orchestrator_task_id: most recent orchestrator task
# ─────────────────────────────────────────────────────────────

@patch("orchestrator.subprocess.run")
def test_get_last_orchestrator_task_id_returns_id(mock_run):  # REQ-22
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout="abc1234 [orchestrator] T02-beta — tests pass, design approved\n",
    )

    task_id = get_last_orchestrator_task_id("/project")

    assert task_id == "T02-beta"


@patch("orchestrator.subprocess.run")
def test_get_last_orchestrator_task_id_returns_none_when_no_commits(mock_run):  # REQ-22
    mock_run.return_value = MagicMock(returncode=0, stdout="")

    task_id = get_last_orchestrator_task_id("/project")

    assert task_id is None


# ─────────────────────────────────────────────────────────────
#  REQ-24  git_reset_hard: removes last commit via git reset --hard HEAD~1
# ─────────────────────────────────────────────────────────────

@patch("orchestrator.subprocess.run")
def test_git_reset_hard_calls_correct_command(mock_run):  # REQ-24
    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

    result = git_reset_hard("/project")

    assert result is True
    call_args = mock_run.call_args
    assert call_args[0][0] == ["git", "reset", "--hard", "HEAD~1"]
    assert call_args[1]["cwd"] == "/project"


# ─────────────────────────────────────────────────────────────
#  REQ-23  resume_check: no prior commits → all tasks, no revert context
# ─────────────────────────────────────────────────────────────

@patch("orchestrator.git_ops.get_completed_task_ids")
def test_resume_check_no_prior_commits_returns_all(mock_ids):  # REQ-23
    mock_ids.return_value = []

    remaining, context = resume_check(_RESUME_TASKS, "pytest", "/project")

    assert remaining == _RESUME_TASKS
    assert context is None


@patch("orchestrator.runner.run_tests")
@patch("orchestrator.git_ops.get_completed_task_ids")
def test_resume_check_green_tests_skip_completed(mock_ids, mock_tests):  # REQ-23
    mock_ids.return_value = ["T01-alpha"]
    mock_tests.return_value = (True, "2 passed")

    remaining, context = resume_check(_RESUME_TASKS, "pytest", "/project")

    assert len(remaining) == 1
    assert remaining[0]["id"] == "T02-beta"
    assert context is None


# ─────────────────────────────────────────────────────────────
#  REQ-24  resume_check: failing tests → reset last commit, return context
# ─────────────────────────────────────────────────────────────

@patch("orchestrator.git_ops.git_reset_hard")
@patch("orchestrator.git_ops.get_last_orchestrator_task_id")
@patch("orchestrator.runner.run_tests")
@patch("orchestrator.git_ops.get_completed_task_ids")
def test_resume_check_failing_tests_resets_and_returns_context(
    mock_ids, mock_tests, mock_last_id, mock_reset,
):  # REQ-24
    mock_ids.return_value = ["T01-alpha", "T02-beta"]
    mock_tests.return_value = (False, "3 failed in 0.5s")
    mock_last_id.return_value = "T02-beta"
    mock_reset.return_value = True

    remaining, context = resume_check(_RESUME_TASKS, "pytest", "/project")

    mock_reset.assert_called_once_with("/project")
    assert any(t["id"] == "T02-beta" for t in remaining)
    assert context is not None
    assert "rolled back" in context.lower()
    assert "3 failed" in context
