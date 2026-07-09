"""Tests for orchestrator.item — unified work-item parser."""
from __future__ import annotations

from pathlib import Path

from orchestrator import item


def _write(p: Path, body: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body, encoding="utf-8")


def test_load_items_recognises_tasks_and_bugs(tmp_path):
    epic = tmp_path / "docs" / "tasks" / "epics" / "E3"
    _write(epic / "T09-table-widget.md", "# T09\n\nGoal: build the table.\n")
    _write(epic / "T11-polling-loop.md", "# T11\n\nGoal: poll every 2s.\n")
    _write(
        epic / "B01-empty-page.md",
        "# B01\n\n**Class:** A\n\n## Symptom\nEmpty.\n",
    )

    items = item.load_items(str(epic))

    ids = {i["id"]: i for i in items}
    assert set(ids) == {"T09-table-widget", "T11-polling-loop", "B01-empty-page"}
    assert ids["T09-table-widget"]["type"] == "task"
    assert ids["T09-table-widget"]["class_"] is None
    assert ids["T09-table-widget"]["epic"] == "E3"
    assert ids["B01-empty-page"]["type"] == "bug"
    assert ids["B01-empty-page"]["class_"] == "A"
    assert ids["B01-empty-page"]["epic"] == "E3"


def test_load_items_reads_class_b(tmp_path):
    epic = tmp_path / "docs" / "tasks" / "epics" / "E5"
    _write(
        epic / "B03-flicker.md",
        "# B03\n\n**Class:** B\n\n## Symptom\nFlickers.\n",
    )

    items = item.load_items(str(epic))
    assert items[0]["class_"] == "B"
    assert items[0]["type"] == "bug"


def test_load_items_skips_templates(tmp_path):
    epics = tmp_path / "docs" / "tasks" / "epics"
    _write(epics / "_TEMPLATE.md", "template body")
    _write(epics / "_TEMPLATE_BUG.md", "bug template body")
    _write(epics / "E1" / "T01-real.md", "# T01\n\nreal task.\n")

    items = item.load_items(str(epics))

    assert [i["id"] for i in items] == ["T01-real"]


def test_load_items_extracts_cross_epic(tmp_path):
    cross = tmp_path / "docs" / "tasks" / "epics" / "cross"
    _write(cross / "B77-shared-code.md", "# B77\n\n**Class:** A\n")

    items = item.load_items(str(cross))
    assert items[0]["epic"] == "cross"


def test_id_prefix_strips_slug():
    assert item.id_prefix("T01-build-and-dependencies") == "T01"
    assert item.id_prefix("B01") == "B01"
    assert item.id_prefix("weird") == "weird"
