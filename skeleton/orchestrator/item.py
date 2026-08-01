"""Unified work-item loader — parses both task files (TASK-<NNNN>-*.md)
and bug files (BUG-<NNNN>-*.md) into a common ``item`` dict, per the
REQ-0006 flat layout convention (workflow-tasks).

Item shape:
    id     : filename stem (e.g. 'TASK-0001-...', 'BUG-0002-...')
    type   : 'task' or 'bug' (from ID prefix)
    class_ : 'A' or 'B' or None (bugs only; parsed from '**Class:**' line)
    epic   : Epic ID (e.g. 'E4-fresh-project-seed-migration') OR the
             literal 'none' (from the file's **Epic:** header field).
             Empty string if the header is absent or malformed.
    content: full markdown text
    path   : absolute file path

The orchestrator only cares about ``type`` (dispatch task vs bug flow),
``class_`` (skip Class B bugs), and ``content`` (the prompt payload).

Note on Epic extraction: under REQ-0006 the flat layout has no
``E<N>/`` subdirectory, so Epic ownership can no longer be read from
the path. It lives in the **Epic:** header field inside the file.
"""
import re
from pathlib import Path

from . import tasks  # reuse for non-directory inputs (json/yaml/single .md)


_BUG_CLASS_RE = re.compile(r"^\*\*Class:\*\*\s*([AB])\b", re.MULTILINE)
_EPIC_HEADER_RE = re.compile(r"^\*\*Epic:\*\*\s*(\S.*?)\s*$", re.MULTILINE)


def load_items(items_path: str) -> list[dict]:
    """Return a list of items from ``items_path``.

    Directory input: recursively finds *.md files (skips ``_TEMPLATE*``,
    ``README.md``, and ``index.md`` — those are scaffolding, not work
    items), classifies each by filename prefix (TASK-… → task,
    BUG-… → bug), and parses the bug's ``Class:`` line and the file's
    ``**Epic:**`` header. Non-directory inputs (json/yaml or a single
    .md file) are delegated to ``tasks.load_tasks`` and marked as
    ``type='task'`` (bug flow is directory-driven).
    """
    path = Path(items_path)

    if path.is_dir():
        items: list[dict] = []
        for f in sorted(path.rglob("*.md")):
            if "_TEMPLATE" in f.name:
                continue
            if f.name in ("index.md", "README.md"):
                continue
            items.append(_item_from_file(f))
        return items

    # Non-directory: fall back to the legacy single-file loader.
    raw = tasks.load_tasks(items_path)
    for r in raw:
        r.setdefault("type", "task")
        r.setdefault("class_", None)
        r.setdefault("epic", "")
    return raw


def _item_from_file(f: Path) -> dict:
    content = f.read_text(encoding="utf-8")
    stem = f.stem
    item_type = "bug" if stem.upper().startswith("BUG-") else "task"
    item: dict = {
        "id":      stem,
        "content": content,
        "path":    str(f),
        "type":    item_type,
        "class_":  _extract_class(content) if item_type == "bug" else None,
        "epic":    _extract_epic_from_header(content),
    }
    return item


def _extract_class(content: str) -> str | None:
    m = _BUG_CLASS_RE.search(content)
    return m.group(1) if m else None


def _extract_epic_from_header(content: str) -> str:
    """Return the **Epic:** header value (e.g. 'E4-fresh-project-seed-migration'
    or 'none'). Empty string if the header is absent or malformed."""
    m = _EPIC_HEADER_RE.search(content)
    return m.group(1).strip() if m else ""


def id_prefix(item_id: str) -> str:
    """Return the ID-only prefix ('TASK-0001', 'BUG-0002', ...) from a
    stem like 'TASK-0001-<slug>'. Used by status.py to align rows
    across the merged index. Non-matching IDs are returned unchanged
    (best-effort).
    """
    m = re.match(r"^((?:TASK|BUG)-\d{4})", item_id)
    return m.group(1) if m else item_id
