"""Tests for orchestrator.item — unified work-item parser (flat REQ-0006 layout)."""
from __future__ import annotations

from pathlib import Path

from orchestrator import item


def _write(p: Path, body: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body, encoding="utf-8")


def test_load_items_recognises_tasks_and_bugs(tmp_path):
    """Flat docs/tasks/ carries TASK-*.md and BUG-*.md side by side.
    Epic ownership comes from the **Epic:** header, NOT from a folder name.
    """
    tasks_dir = tmp_path / "docs" / "tasks"
    _write(
        tasks_dir / "TASK-0009-table-widget.md",
        "# TASK-0009\n\n**Epic:** E3-live-status-view\n\nGoal: build the table.\n",
    )
    _write(
        tasks_dir / "TASK-0011-polling-loop.md",
        "# TASK-0011\n\n**Epic:** E3-live-status-view\n\nGoal: poll every 2s.\n",
    )
    _write(
        tasks_dir / "BUG-0001-empty-page.md",
        "# BUG-0001\n\n**Epic:** E3-live-status-view\n**Class:** A\n\n## Symptom\nEmpty.\n",
    )

    items = item.load_items(str(tasks_dir))

    ids = {i["id"]: i for i in items}
    assert set(ids) == {"TASK-0009-table-widget", "TASK-0011-polling-loop", "BUG-0001-empty-page"}
    assert ids["TASK-0009-table-widget"]["type"] == "task"
    assert ids["TASK-0009-table-widget"]["class_"] is None
    assert ids["TASK-0009-table-widget"]["epic"] == "E3-live-status-view"
    assert ids["BUG-0001-empty-page"]["type"] == "bug"
    assert ids["BUG-0001-empty-page"]["class_"] == "A"
    assert ids["BUG-0001-empty-page"]["epic"] == "E3-live-status-view"


def test_load_items_reads_class_b(tmp_path):
    tasks_dir = tmp_path / "docs" / "tasks"
    _write(
        tasks_dir / "BUG-0003-flicker.md",
        "# BUG-0003\n\n**Epic:** E5-frontend\n**Class:** B\n\n## Symptom\nFlickers.\n",
    )

    items = item.load_items(str(tasks_dir))
    assert items[0]["class_"] == "B"
    assert items[0]["type"] == "bug"
    assert items[0]["epic"] == "E5-frontend"


def test_load_items_skips_templates_and_scaffolding(tmp_path):
    """_TEMPLATE_*.md, README.md, index.md are scaffolding, not work items."""
    tasks_dir = tmp_path / "docs" / "tasks"
    _write(tasks_dir / "_TEMPLATE_TASK.md", "template body")
    _write(tasks_dir / "_TEMPLATE_BUG.md", "bug template body")
    _write(tasks_dir / "README.md", "orientation body")
    _write(tasks_dir / "index.md", "| ID | Title | Status |")
    _write(
        tasks_dir / "TASK-0001-real.md",
        "# TASK-0001\n\n**Epic:** E1-foundation\n\nreal task.\n",
    )

    items = item.load_items(str(tasks_dir))

    assert [i["id"] for i in items] == ["TASK-0001-real"]


def test_load_items_epic_none_when_header_missing(tmp_path):
    """A file without an **Epic:** header returns empty-string epic (best-effort)."""
    tasks_dir = tmp_path / "docs" / "tasks"
    _write(tasks_dir / "TASK-0077-no-header.md", "# TASK-0077\n\nNo Epic header here.\n")

    items = item.load_items(str(tasks_dir))
    assert items[0]["epic"] == ""


def test_load_items_epic_literal_none(tmp_path):
    """**Epic:** none is a valid value for cross-Epic / project-wide items."""
    tasks_dir = tmp_path / "docs" / "tasks"
    _write(
        tasks_dir / "BUG-0077-shared-code.md",
        "# BUG-0077\n\n**Epic:** none\n**Class:** A\n",
    )

    items = item.load_items(str(tasks_dir))
    assert items[0]["epic"] == "none"


def test_id_prefix_strips_slug():
    assert item.id_prefix("TASK-0001-build-and-dependencies") == "TASK-0001"
    assert item.id_prefix("BUG-0002-something-broke") == "BUG-0002"
    assert item.id_prefix("TASK-0099") == "TASK-0099"
    assert item.id_prefix("weird") == "weird"
