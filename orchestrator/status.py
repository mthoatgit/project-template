"""`docs/tasks/index.md` maintenance — the ``update_task_status`` flow (REQ-38)."""
import re
from pathlib import Path

STATUS_REL_PATH = Path("docs") / "tasks" / "index.md"
_STATUS_VALUES = ("pending", "in progress", "done", "action needed")
STATUS_WIDTH = max(len(v) for v in _STATUS_VALUES)  # 13 ('action needed')

# A task-row Status cell: everything up to the last '|' before the value,
# then the value itself, then optional trailing padding, then the closing '|'.
# The task ID may be bare ('T01') or slug-suffixed ('T01-foo') in the row.
_STATUS_ROW_RE = re.compile(
    r"(?P<prefix>^\|\s*(?P<id>T\d+)(?:-\S*)?\s*\|[^|\n]*\|[^|\n]*\|\s*)"
    r"(?P<status>pending|in progress|done|action needed)"
    r"\s*(?P<close>\|)",
    re.MULTILINE,
)


def update_task_status(project_dir: str, task_id: str, new_status: str) -> bool:
    """Rewrite the Status cell for ``task_id`` in ``docs/tasks/index.md``.

    Matches the row whose ID cell is exactly the task ID's numeric prefix
    (e.g. 'T01' matches both 'T01' and input 'T01-foo'). Missing file or
    unmatched ID → warn and return False; the orchestrator continues
    regardless (status maintenance is best-effort). The written status
    is padded to ``STATUS_WIDTH`` so column alignment survives writes.
    """
    if new_status not in _STATUS_VALUES:
        raise ValueError(f"invalid status {new_status!r}; expected one of {_STATUS_VALUES}")

    path = Path(project_dir) / STATUS_REL_PATH
    if not path.exists():
        print(f"  [status] {STATUS_REL_PATH.as_posix()} not found — skipping status update")
        return False

    m = re.match(r"^(T\d+)", task_id)
    if not m:
        print(f"  [status] cannot extract numeric ID from '{task_id}' — skipping")
        return False
    short_id = m.group(1)

    original = path.read_text(encoding="utf-8")
    padded = new_status.ljust(STATUS_WIDTH)
    matched = False

    def _replace(match: "re.Match[str]") -> str:
        nonlocal matched
        if match.group("id") != short_id:
            return match.group(0)
        matched = True
        return f"{match.group('prefix')}{padded} {match.group('close')}"

    updated = _STATUS_ROW_RE.sub(_replace, original)
    if not matched:
        print(f"  [status] no row for '{short_id}' — skipping status update")
        return False

    if updated != original:
        path.write_text(updated, encoding="utf-8")
    return True
