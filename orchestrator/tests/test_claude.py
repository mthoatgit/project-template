"""Tests for orchestrator.claude — Claude CLI invocation (REQ-27),
session-limit auto-resume (REQ-28), and the subprocess guardrail settings
(REQ-39, REQ-41)."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from orchestrator import handle_session_limit, parse_reset_time, run_claude

from orchestrator.tests.helpers import _mock_popen


# ─────────────────────────────────────────────────────────────
#  REQ-27  run_claude passes --dangerously-skip-permissions + --settings
# ─────────────────────────────────────────────────────────────

@patch("orchestrator.subprocess.Popen")
def test_run_claude_passes_dangerously_skip_permissions(mock_popen):  # REQ-27
    mock_popen.return_value = _mock_popen(returncode=0, output="done\n")

    run_claude("implement this", "/project")

    cmd = mock_popen.call_args_list[0][0][0]
    assert "--dangerously-skip-permissions" in cmd
    assert "-p" in cmd
    assert "implement this" in cmd


@patch("orchestrator.subprocess.Popen")
def test_run_claude_passes_settings_file(mock_popen):  # REQ-39, REQ-41
    """Every subprocess Claude call receives --settings pointing at the
    package's subprocess_settings.json — the file that ships the deny
    list (no post-hoc rollback lives in claude.py anymore)."""
    mock_popen.return_value = _mock_popen(returncode=0, output="done\n")

    run_claude("implement this", "/project")

    cmd = mock_popen.call_args_list[0][0][0]
    assert "--settings" in cmd
    settings_arg = cmd[cmd.index("--settings") + 1]
    settings_path = Path(settings_arg)
    assert settings_path.name == "subprocess_settings.json"
    # File must actually exist so the CLI can load it.
    assert settings_path.exists(), f"missing settings file at {settings_path}"


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
#  REQ-39 / REQ-41  Subprocess guardrail — deny list in the shipped
#                   settings file (no post-hoc rollback anymore).
# ─────────────────────────────────────────────────────────────

def _settings() -> dict:
    """Load the shipped subprocess_settings.json used by run_claude."""
    from orchestrator.claude import _SETTINGS_PATH
    return json.loads(Path(_SETTINGS_PATH).read_text(encoding="utf-8"))


def test_subprocess_settings_deny_git_write_commands():  # REQ-41
    """The commands that would create commits (or otherwise rewrite git
    history) are hard-blocked. Bash and PowerShell must both be covered
    because run_tests uses PowerShell on Windows."""
    deny = _settings()["permissions"]["deny"]
    for cmd in ("git commit", "git revert", "git merge", "git cherry-pick",
                "git rebase", "git reset", "git push"):
        assert f"Bash({cmd}*)" in deny, f"Bash deny missing: {cmd}"
        assert f"PowerShell({cmd}*)" in deny, f"PowerShell deny missing: {cmd}"


def test_subprocess_settings_deny_orchestrator_file_writes():  # REQ-39
    """Every write path that Claude typically uses for source files is
    blocked from touching anything under orchestrator/.

    A single ``Edit(orchestrator/**)`` rule is sufficient — Claude Code's
    permission model treats Edit as the umbrella tool that covers Write,
    MultiEdit, and any other file-editing tool. Adding separate
    ``Write(...)`` / ``MultiEdit(...)`` entries produces "not matched by
    file permission checks" warnings on every subprocess call (see
    backlog item 015). Assert only ``Edit(...)`` and assert that the
    other two are absent so the warning cannot regress.
    """
    deny = _settings()["permissions"]["deny"]
    assert "Edit(orchestrator/**)" in deny, "deny missing: Edit(orchestrator/**)"
    for shadow in ("Write(orchestrator/**)", "MultiEdit(orchestrator/**)"):
        assert shadow not in deny, (
            f"{shadow} is a no-op — Edit(...) already covers it, and the "
            f"presence of {shadow} produces a CLI warning every call"
        )
