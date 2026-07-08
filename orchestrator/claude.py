"""Claude Code CLI wrapper — invocation (REQ-27), session-limit auto-resume
(REQ-28), and the protected-file guardrail (REQ-39)."""
import re
import subprocess
import sys

from .config import PROTECTED_FILES

# ── Session-limit handling (REQ-28) ────────────────────────────
# Edit parse_reset_time() if Claude changes the message format.
_SESSION_LIMIT_MARKER = "session limit"
_RESET_PATTERN = re.compile(
    r"resets\s+(\d{1,2}:\d{2}\s*(?:am|pm))\s*\(([^)]+)\)",
    re.IGNORECASE,
)


def parse_reset_time(message: str):
    """Parse ``'resets 11:40am (Europe/Berlin)'`` → datetime, or None.

    Returns an aware datetime when the IANA timezone database is available
    (Linux/Mac or Windows+tzdata). Falls back to a naive local-time datetime
    when timezone resolution fails — Claude displays times in the user's
    local timezone anyway, so the sleep duration is still accurate.
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


# ── Protected-file guardrail (REQ-39) ──────────────────────────

def _revert_touched_protected_files(project_dir: str) -> list[str]:
    """Revert any modifications to PROTECTED_FILES in the working tree (REQ-39).

    Compares against HEAD so any diff — from Claude, from an editor, from
    any source — is undone. Returns the list of files that were reverted
    (empty if none were touched, or if the project has no git repo).
    Untracked files are ignored (``git checkout`` can't revert them, and
    PROTECTED_FILES are always tracked in a project that ships them).

    The pathspec ``orchestrator`` matches everything under the directory,
    so a nested edit to e.g. ``orchestrator/config.py`` is caught.
    """
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD", "--"] + list(PROTECTED_FILES),
            cwd=project_dir, capture_output=True, text=True, encoding="utf-8",
        )
    except Exception:
        return []  # git unavailable, cwd missing, or subprocess mocked in tests
    if result.returncode != 0:
        return []  # not a git repo — nothing to guard
    touched = sorted(f for f in result.stdout.splitlines() if f)
    if not touched:
        return []
    subprocess.run(
        ["git", "checkout", "HEAD", "--"] + touched,
        cwd=project_dir, capture_output=True, text=True,
    )
    return touched


def run_claude(prompt: str, project_dir: str) -> tuple[int, str]:
    """Call the Claude Code CLI in non-interactive (print) mode.

    Output is streamed line-by-line (prefixed with ``  │ ``) so the log
    file updates in real time during long Claude calls instead of staying
    silent for several minutes.

    After every call, PROTECTED_FILES modifications are reverted (REQ-39).
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
        reverted = _revert_touched_protected_files(project_dir)
        if reverted:
            print(
                f"  [!] GUARDRAIL: reverted Claude edits to protected file(s): "
                f"{', '.join(reverted)}"
            )
        return proc.returncode, output
