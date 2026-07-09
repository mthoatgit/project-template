"""Unified work-item loader — parses both task files (T<NN>-*.md) and
bug files (B<NN>-*.md) into a common ``item`` dict.

Item shape:
    id     : filename stem (e.g. 'T01-...', 'B01-...')
    type   : 'task' or 'bug' (from ID prefix)
    class_ : 'A' or 'B' or None (bugs only; parsed from '**Class:**' line)
    epic   : 'E<N>' or 'cross' or '' (from path)
    content: full markdown text
    path   : absolute file path

The orchestrator only cares about ``type`` (dispatch task vs bug flow),
``class_`` (skip Class B bugs), and ``content`` (the prompt payload).
"""
import re
from pathlib import Path

from . import tasks  # reuse for non-directory inputs (json/yaml/single .md)


_BUG_CLASS_RE = re.compile(r"^\*\*Class:\*\*\s*([AB])\b", re.MULTILINE)


def load_items(items_path: str) -> list[dict]:
    """Return a list of items from ``items_path``.

    Directory input: recursively finds *.md files (skips ``_TEMPLATE*``),
    classifies each by filename prefix (T… → task, B… → bug), and
    parses the bug's ``Class:`` line. Non-directory inputs (json/yaml
    or a single .md file) are delegated to ``tasks.load_tasks`` and
    marked as ``type='task'`` (bug flow is directory-driven).
    """
    path = Path(items_path)

    if path.is_dir():
        items: list[dict] = []
        for f in sorted(path.rglob("*.md")):
            if "_TEMPLATE" in f.name:
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
    item_type = "bug" if stem.upper().startswith("B") else "task"
    item: dict = {
        "id":      stem,
        "content": content,
        "path":    str(f),
        "type":    item_type,
        "class_":  _extract_class(content) if item_type == "bug" else None,
        "epic":    _extract_epic_from_path(f),
    }
    return item


def _extract_class(content: str) -> str | None:
    m = _BUG_CLASS_RE.search(content)
    return m.group(1) if m else None


def _extract_epic_from_path(f: Path) -> str:
    for part in f.parts:
        if re.match(r"^E\d+$", part, re.IGNORECASE):
            return part.upper()
        if part.lower() == "cross":
            return "cross"
    return ""


def id_prefix(item_id: str) -> str:
    """Return the ID-only prefix ('T01', 'B02', ...) from a stem like
    'T01-<slug>'. Used by status.py to align rows across the merged
    index. Non-matching IDs are returned unchanged (best-effort)."""
    m = re.match(r"^([TB]\d+)", item_id)
    return m.group(1) if m else item_id
