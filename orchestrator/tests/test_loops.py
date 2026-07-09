"""Tests for orchestrator.loops — ralph_loop, critic_loop, write_tests_phase
(REQ-08..20, REQ-30/31 abort path, REQ-38 status flips)."""
from __future__ import annotations

from unittest.mock import patch

from orchestrator import (
    STUCK_STREAK_THRESHOLD,
    critic_loop,
    ralph_loop,
    write_tests_phase,
)

from orchestrator.tests.helpers import TASK


# ─────────────────────────────────────────────────────────────
#  REQ-08  passes on first attempt
#  REQ-09  passes after fix attempt
# ─────────────────────────────────────────────────────────────

@patch("orchestrator.runner.run_tests")
@patch("orchestrator.claude.run_claude")
def test_passes_on_first_attempt(mock_claude, mock_tests):  # REQ-08
    mock_claude.return_value = (0, "implemented")
    mock_tests.return_value  = (True, "1 passed in 0.1s")

    assert ralph_loop(TASK, "pytest", "/project", max_iterations=5) is True
    assert mock_claude.call_count == 1
    assert mock_tests.call_count  == 1


@patch("orchestrator.runner.run_tests")
@patch("orchestrator.claude.run_claude")
def test_passes_after_one_retry(mock_claude, mock_tests):  # REQ-09
    mock_claude.return_value = (0, "fixed")
    mock_tests.side_effect   = [
        (False, "2 failed in 0.3s"),
        (True,  "2 passed in 0.3s"),
    ]

    assert ralph_loop(TASK, "pytest", "/project", max_iterations=5) is True
    assert mock_claude.call_count == 2
    assert mock_tests.call_count  == 2


# ─────────────────────────────────────────────────────────────
#  REQ-10  criterion 1 — identical output
# ─────────────────────────────────────────────────────────────

@patch("orchestrator.runner.run_tests")
@patch("orchestrator.claude.run_claude")
def test_exit_identical_output(mock_claude, mock_tests):  # REQ-10
    mock_claude.return_value = (0, "")
    mock_tests.return_value  = (False, "3 failed, AssertionError")

    assert ralph_loop(TASK, "pytest", "/project", max_iterations=5) is False
    assert mock_tests.call_count == 2  # iter 0 sets baseline, iter 1 matches → stop


# ─────────────────────────────────────────────────────────────
#  REQ-11  criterion 2 — stuck streak
#  REQ-12  criterion 2 — streak resets on progress
# ─────────────────────────────────────────────────────────────

@patch("orchestrator.runner.run_tests")
@patch("orchestrator.claude.run_claude")
def test_exit_stuck_streak(mock_claude, mock_tests):  # REQ-11
    mock_claude.return_value = (0, "tweaked code")
    mock_tests.side_effect = [
        (False, f"2 failed, attempt {i}, different message") for i in range(10)
    ]

    assert ralph_loop(TASK, "pytest", "/project", max_iterations=5) is False
    # iter 0: count=2, streak=0
    # iter 1: count=2, streak=1  (< threshold)
    # iter 2: count=2, streak=2  (>= threshold → stop)
    assert mock_tests.call_count == STUCK_STREAK_THRESHOLD + 1


@patch("orchestrator.runner.run_tests")
@patch("orchestrator.claude.run_claude")
def test_stuck_streak_resets_on_progress(mock_claude, mock_tests):  # REQ-12
    mock_claude.return_value = (0, "fixed")
    mock_tests.side_effect = [
        (False, "3 failed, attempt 0"),  # iter 0: count=3
        (False, "3 failed, attempt 1"),  # iter 1: count=3, streak=1
        (False, "2 failed, attempt 2"),  # iter 2: count=2, streak resets to 0
        (True,  "2 passed in 0.5s"),     # iter 3: pass
    ]

    assert ralph_loop(TASK, "pytest", "/project", max_iterations=5) is True
    assert mock_tests.call_count == 4


# ─────────────────────────────────────────────────────────────
#  REQ-13  criterion 3 — regression
# ─────────────────────────────────────────────────────────────

@patch("orchestrator.runner.run_tests")
@patch("orchestrator.claude.run_claude")
def test_exit_regression(mock_claude, mock_tests):  # REQ-13
    mock_claude.return_value = (0, "attempted fix")
    mock_tests.side_effect = [
        (False, "1 failed in 0.2s"),  # iter 0: 1 failure
        (False, "3 failed in 0.2s"),  # iter 1: regression to 3
    ]

    assert ralph_loop(TASK, "pytest", "/project", max_iterations=5) is False
    assert mock_tests.call_count == 2


# ─────────────────────────────────────────────────────────────
#  REQ-14  criterion 4 — max iterations
# ─────────────────────────────────────────────────────────────

@patch("orchestrator.runner.run_tests")
@patch("orchestrator.claude.run_claude")
def test_exit_max_iterations(mock_claude, mock_tests):  # REQ-14
    max_iter = 3
    mock_claude.return_value = (0, "incremental fix")
    mock_tests.side_effect = [
        (False, f"{10 - i} failed, iteration {i}") for i in range(max_iter + 1)
    ]

    assert ralph_loop(TASK, "pytest", "/project", max_iterations=max_iter) is False
    assert mock_tests.call_count == max_iter + 1


# ─────────────────────────────────────────────────────────────
#  REQ-15  critic runs after tests pass
# ─────────────────────────────────────────────────────────────

@patch("orchestrator.runner.run_tests")
@patch("orchestrator.claude.run_claude")
def test_critic_runs_after_tests_pass(mock_claude, mock_tests):  # REQ-15
    # First call: implementation; second call: critic review
    mock_claude.side_effect = [
        (0, "implemented"),           # ralph_loop: implement
        (0, "APPROVED — clean"),      # critic review
    ]
    mock_tests.return_value = (True, "1 passed")

    result = critic_loop(TASK, "pytest", "/project", max_ralph_iterations=5, max_critic_iterations=3)

    assert result is True
    assert mock_claude.call_count == 2  # implement + critic


# ─────────────────────────────────────────────────────────────
#  REQ-18  re-implementation feeds Critic feedback back to Claude
# ─────────────────────────────────────────────────────────────

@patch("orchestrator.runner.run_tests")
@patch("orchestrator.claude.run_claude")
def test_critic_rejection_triggers_reimplementation_with_feedback(mock_claude, mock_tests):  # REQ-18
    weakness = "- Uses procedural style instead of appropriate OOP pattern"
    mock_claude.side_effect = [
        (0, "first implementation"),           # cycle 1: implement
        (0, f"REJECTED\n{weakness}"),          # cycle 1: critic rejects
        (0, "second implementation"),          # cycle 2: re-implement
        (0, "APPROVED — now uses OOP"),        # cycle 2: critic approves
    ]
    mock_tests.return_value = (True, "all passed")

    result = critic_loop(TASK, "pytest", "/project", max_ralph_iterations=5, max_critic_iterations=3)

    assert result is True
    # The third claude call (re-implementation) must include critic feedback
    third_call_prompt = mock_claude.call_args_list[2][0][0]
    assert weakness in third_call_prompt


# ─────────────────────────────────────────────────────────────
#  REQ-19  critic stuck detection — same feedback twice
# ─────────────────────────────────────────────────────────────

@patch("orchestrator.runner.run_tests")
@patch("orchestrator.claude.run_claude")
def test_critic_loop_aborts_on_repeated_feedback(mock_claude, mock_tests):  # REQ-19
    weakness = "- Wrong abstraction level throughout"
    mock_claude.side_effect = [
        (0, "implementation v1"),       # cycle 1: implement
        (0, f"REJECTED\n{weakness}"),   # cycle 1: critic rejects
        (0, "implementation v2"),       # cycle 2: re-implement
        (0, f"REJECTED\n{weakness}"),   # cycle 2: same feedback → stuck
    ]
    mock_tests.return_value = (True, "all passed")

    result = critic_loop(TASK, "pytest", "/project", max_ralph_iterations=5, max_critic_iterations=3)

    assert result is False
    assert mock_claude.call_count == 4


# ─────────────────────────────────────────────────────────────
#  REQ-20  critic loop max iterations
# ─────────────────────────────────────────────────────────────

@patch("orchestrator.runner.run_tests")
@patch("orchestrator.claude.run_claude")
def test_critic_loop_max_iterations(mock_claude, mock_tests):  # REQ-20
    max_critic = 2
    mock_claude.side_effect = [
        (0, f"implementation {i // 2}") if i % 2 == 0
        else (0, f"REJECTED\n- concern {i}")   # different feedback each time
        for i in range((max_critic + 1) * 2)
    ]
    mock_tests.return_value = (True, "all passed")

    result = critic_loop(TASK, "pytest", "/project", max_ralph_iterations=5,
                         max_critic_iterations=max_critic)

    assert result is False
    # implement + critic per cycle, cycles = max_critic + 1
    assert mock_claude.call_count == (max_critic + 1) * 2


@patch("orchestrator.runner.run_tests")
@patch("orchestrator.claude.run_claude")
def test_critic_loop_fails_if_ralph_loop_fails(mock_claude, mock_tests):  # REQ-20
    mock_claude.return_value = (0, "")
    mock_tests.return_value = (False, "3 failed, identical every time")

    result = critic_loop(TASK, "pytest", "/project", max_ralph_iterations=5, max_critic_iterations=3)

    assert result is False


# ─────────────────────────────────────────────────────────────
#  REQ-25  task marked failed if retry with revert context still cannot fix
# ─────────────────────────────────────────────────────────────

@patch("orchestrator.runner.run_tests")
@patch("orchestrator.claude.run_claude")
def test_task_marked_failed_when_retry_cannot_fix(mock_claude, mock_tests):  # REQ-25
    mock_claude.return_value = (0, "")
    mock_tests.return_value = (False, "5 failed, tests still broken")

    result = critic_loop(
        TASK, "pytest", "/project",
        max_ralph_iterations=5, max_critic_iterations=3,
        revert_context="Previous commit caused 5 failures",
    )

    assert result is False


# ─────────────────────────────────────────────────────────────
#  REQ-31  write_tests_phase: fails task when no files created
# ─────────────────────────────────────────────────────────────

@patch("orchestrator.runner.detect_task_test_files", return_value=[])
@patch("orchestrator.claude.run_claude", return_value=(0, "wrote nothing"))
def test_write_tests_phase_fails_when_no_files_created(mock_claude, mock_detect):  # REQ-31
    cmd, ok = write_tests_phase(TASK, "pytest tests/", "# doc", "/project")

    assert ok is False
    assert cmd == "pytest tests/"  # original cmd returned unchanged


# ─────────────────────────────────────────────────────────────
#  REQ-38  critic_loop flips index.md status through the lifecycle
# ─────────────────────────────────────────────────────────────

@patch("orchestrator.status.update_task_status")
@patch("orchestrator.claude.run_claude")
@patch("orchestrator.runner.run_tests")
def test_critic_loop_flips_status_to_done_on_success(  # REQ-38
    mock_tests, mock_claude, mock_update, tmp_path,
):
    mock_tests.return_value = (True, "pytest: 3 passed")
    mock_claude.return_value = (0, "APPROVED — looks great")

    ok = critic_loop(TASK, "pytest", str(tmp_path), max_ralph_iterations=1, max_critic_iterations=1)

    assert ok is True
    calls = [c.args for c in mock_update.call_args_list]
    assert (str(tmp_path), TASK["id"], "in progress") in calls
    assert (str(tmp_path), TASK["id"], "done") in calls


@patch("orchestrator.status.update_task_status")
@patch("orchestrator.claude.run_claude")
@patch("orchestrator.runner.run_tests")
def test_critic_loop_flips_status_to_action_needed_on_failure(  # REQ-38
    mock_tests, mock_claude, mock_update, tmp_path,
):
    # tests never pass → ralph_loop returns False → critic_loop returns False
    mock_tests.return_value = (False, "pytest: 3 failed")
    mock_claude.return_value = (0, "")

    ok = critic_loop(TASK, "pytest", str(tmp_path), max_ralph_iterations=1, max_critic_iterations=1)

    assert ok is False
    calls = [c.args for c in mock_update.call_args_list]
    assert (str(tmp_path), TASK["id"], "in progress") in calls
    assert (str(tmp_path), TASK["id"], "action needed") in calls
