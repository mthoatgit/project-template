"""Tests for orchestrator.claude — Claude CLI invocation (REQ-27),
session-limit auto-resume (REQ-28), and the protected-file guardrail (REQ-39)."""
from __future__ import annotations

from datetime import datetime
from unittest.mock import patch

from orchestrator import (
    _revert_touched_protected_files,
    handle_session_limit,
    parse_reset_time,
    run_claude,
)

from orchestrator.tests.helpers import _make_git_repo, _mock_popen


# ─────────────────────────────────────────────────────────────
#  REQ-27  run_claude passes --dangerously-skip-permissions
# ─────────────────────────────────────────────────────────────

@patch("orchestrator.subprocess.Popen")
def test_run_claude_passes_dangerously_skip_permissions(mock_popen):  # REQ-27
    mock_popen.return_value = _mock_popen(returncode=0, output="done\n")

    run_claude("implement this", "/project")

    # First Popen call is the claude CLI (later calls come from the REQ-39
    # protected-file guardrail that runs 'git diff' / 'git checkout').
    cmd = mock_popen.call_args_list[0][0][0]
    assert "--dangerously-skip-permissions" in cmd
    assert "-p" in cmd
    assert "implement this" in cmd


# ─────────────────────────────────────────────────────────────
#  REQ-28  session-limit detection and auto-resume
# ─────────────────────────────────────────────────────────────

def test_parse_reset_time_returns_none_for_unparseable():  # REQ-28
    assert parse_reset_time("some unrelated error") is None


def test_parse_reset_time_returns_future_datetime():  # REQ-28
    msg = "You've hit your session limit · resets 11:40am (Europe/Berlin)"
    result = parse_reset_time(msg)
    assert result is not None
    now = datetime.now(result.tzinfo) if result.tzinfo else datetime.now()
    assert result > now


@patch("orchestrator.subprocess.Popen")
@patch("orchestrator.claude.handle_session_limit")
def test_run_claude_detects_session_limit_and_retries(mock_handle, mock_popen):  # REQ-28
    limit_msg = "You've hit your session limit · resets 11:40am (Europe/Berlin)\n"
    mock_popen.side_effect = [
        _mock_popen(returncode=1, output=limit_msg),
        _mock_popen(returncode=0, output="done\n"),
    ]
    rc, output = run_claude("implement this", "/project")
    assert mock_handle.call_count == 1
    assert rc == 0
    assert output == "done"


@patch("orchestrator.claude.sys.exit")
@patch("orchestrator.claude.parse_reset_time", return_value=None)
def test_handle_session_limit_exits_2_when_unparseable(mock_parse, mock_exit):  # REQ-28
    handle_session_limit("session limit hit, no time info")
    mock_exit.assert_called_once_with(2)


# ─────────────────────────────────────────────────────────────
#  REQ-39  Protected-file guardrail
# ─────────────────────────────────────────────────────────────

def test_revert_touched_protected_files_reverts_orchestrator_module(tmp_path):  # REQ-39
    """Editing a file under orchestrator/ triggers a revert; unrelated files don't."""
    (tmp_path / "orchestrator").mkdir()
    _make_git_repo(tmp_path, {
        "orchestrator/config.py": "MAX = 5\n",
        "backend.py":             "original\n",
    })
    (tmp_path / "orchestrator" / "config.py").write_text("MAX = 999  # HIJACKED\n", encoding="utf-8")

    reverted = _revert_touched_protected_files(str(tmp_path))

    assert reverted == ["orchestrator/config.py"]
    assert (tmp_path / "orchestrator" / "config.py").read_text(encoding="utf-8") == "MAX = 5\n"


def test_revert_touched_protected_files_ignores_other_changes(tmp_path):  # REQ-39
    (tmp_path / "orchestrator").mkdir()
    _make_git_repo(tmp_path, {
        "orchestrator/config.py": "MAX = 5\n",
        "backend.py":             "original\n",
    })
    (tmp_path / "backend.py").write_text("legitimate change\n", encoding="utf-8")

    reverted = _revert_touched_protected_files(str(tmp_path))

    assert reverted == []
    assert (tmp_path / "backend.py").read_text(encoding="utf-8") == "legitimate change\n"


def test_revert_touched_protected_files_reverts_both_when_both_touched(tmp_path):  # REQ-39
    (tmp_path / "orchestrator").mkdir()
    _make_git_repo(tmp_path, {
        "orchestrator/main.py":   "main original\n",
        "test_orchestrator.py":   "test original\n",
    })
    (tmp_path / "orchestrator" / "main.py").write_text("main HIJACKED\n", encoding="utf-8")
    (tmp_path / "test_orchestrator.py").write_text("test HIJACKED\n", encoding="utf-8")

    reverted = _revert_touched_protected_files(str(tmp_path))

    assert reverted == ["orchestrator/main.py", "test_orchestrator.py"]
    assert (tmp_path / "orchestrator" / "main.py").read_text(encoding="utf-8") == "main original\n"
    assert (tmp_path / "test_orchestrator.py").read_text(encoding="utf-8") == "test original\n"


def test_revert_touched_protected_files_no_git_repo_returns_empty(tmp_path):  # REQ-39
    # tmp_path is not a git repo
    (tmp_path / "orchestrator").mkdir()
    (tmp_path / "orchestrator" / "config.py").write_text("anything\n", encoding="utf-8")
    assert _revert_touched_protected_files(str(tmp_path)) == []
