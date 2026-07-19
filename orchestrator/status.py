"""``docs/tasks/index.md`` maintenance — the ``update_task_status`` flow (REQ-38).

The merged work-item index (tasks + bugs) has five columns:
    | ID  | Epic | Type | Title | Status |

This module rewrites the Status cell for a given item id (T… or B…).
It does not care about Type — that dispatch is done upstream in main.py.
"""
import re
from pathlib import Path

STATUS_REL_PATH = Path("docs") / "tasks" / "index.md"
_STATUS_VALUES = ("pending", "in progress", "done", "action needed")
STATUS_WIDTH = max(len(v) for v in _STATUS_VALUES)  # 13 ('action needed')

# Canonical width of the Status cell content (between the two `|` chars):
# 1 leading space + STATUS_WIDTH + 1 trailing space.
_STATUS_CELL_WIDTH = STATUS_WIDTH + 2

# A work-item-row Status cell:
#   |  ID  | Epic | Type | Title | Status |
# The ID cell may be bare ('T01', 'B01') or slug-suffixed ('T01-foo').
# Three intermediate cells (Epic, Type, Title) — captured as [^|\n]* runs —
# then the Status value, then optional trailing padding, then the close pipe.
_STATUS_ROW_RE = re.compile(
    r"(?P<prefix>^\|\s*(?P<id>[TB]\d+)(?:-\S*)?\s*\|[^|\n]*\|[^|\n]*\|[^|\n]*\|\s*)"
    r"(?P<status>pending|in progress|done|action needed)"
    r"\s*(?P<close>\|)",
    re.MULTILINE,
)


def update_task_status(project_dir: str, task_id: str, new_status: str) -> bool:
    """Rewrite the Status cell for ``task_id`` in ``docs/tasks/index.md``.

    Matches the row whose ID cell is exactly the item's short ID (e.g.
    'T01' or 'B01' — matches both bare and slug-suffixed rows). Missing
    file or unmatched ID → warn and return False; the orchestrator
    continues regardless (status maintenance is best-effort). The
    written status is padded to ``STATUS_WIDTH`` so column alignment
    survives writes.
    """
    if new_status not in _STATUS_VALUES:
        raise ValueError(f"invalid status {new_status!r}; expected one of {_STATUS_VALUES}")

    path = Path(project_dir) / STATUS_REL_PATH
    if not path.exists():
        print(f"  [status] {STATUS_REL_PATH.as_posix()} not found — skipping status update")
        return False

    m = re.match(r"^([TB]\d+)", task_id)
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

    # Self-heal: a hand-written or scaffold-generated index.md may have a
    # narrower Status header/separator than the data rows require after
    # padding — widen (never shrink) so the table stays aligned. See
    # backlog item 030 #5.
    updated = _widen_status_column_header(updated)

    if updated != original:
        path.write_text(updated, encoding="utf-8")
    return True


def _widen_status_column_header(text: str) -> str:
    """If the Status column's header cell or separator cell is narrower
    than ``_STATUS_CELL_WIDTH``, widen it to that width. Only the LAST
    column of a table whose header cell is literally ``Status`` is
    touched. Widen-only: existing wider cells are left alone.
    """
    lines = text.splitlines(keepends=True)
    for i, line in enumerate(lines):
        body = line.rstrip("\r\n")
        eol = line[len(body):]
        if not (body.startswith("|") and body.endswith("|")):
            continue
        cells = body.split("|")
        # split("|") on "|a|b|" → ['', 'a', 'b', ''] — first/last are empty.
        if len(cells) < 3 or cells[-2].strip() != "Status":
            continue
        # Widen the header cell if too narrow.
        if len(cells[-2]) < _STATUS_CELL_WIDTH:
            cells[-2] = " " + "Status".ljust(STATUS_WIDTH) + " "
            lines[i] = "|".join(cells) + eol
        # Widen the immediate following separator row if present + too narrow.
        if i + 1 < len(lines):
            sep_line = lines[i + 1]
            sep_body = sep_line.rstrip("\r\n")
            sep_eol = sep_line[len(sep_body):]
            if sep_body.startswith("|") and "---" in sep_body:
                sep_cells = sep_body.split("|")
                if (len(sep_cells) == len(cells)
                        and set(sep_cells[-2].strip()) <= {"-", ":"}
                        and len(sep_cells[-2]) < _STATUS_CELL_WIDTH):
                    sep_cells[-2] = "-" * _STATUS_CELL_WIDTH
                    lines[i + 1] = "|".join(sep_cells) + sep_eol
        break  # header handled; other tables in the file are none of our business
    return "".join(lines)
