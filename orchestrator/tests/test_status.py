"""Tests for orchestrator.status — docs/index.md rewriting (REQ-38)."""
from __future__ import annotations

import pytest

from orchestrator import update_task_status

from orchestrator.tests.helpers import _make_index, _row_for


def test_update_task_status_flips_pending_to_in_progress(tmp_path):  # REQ-38
    f = _make_index(tmp_path)

    assert update_task_status(str(tmp_path), "TASK-0001-build", "in progress") is True

    row = _row_for(f, "TASK-0001")
    assert "in progress" in row
    # pipe positions unchanged (status padded to 13 chars = 'action needed')
    # Merged index has 5 columns → 6 pipes per row.
    assert row.count("|") == 6
    assert "| in progress   |" in row
    # sibling row untouched
    assert "| TASK-0002 | E1   | task | Docker compose stack   | pending       |" in f.read_text(encoding="utf-8")


def test_update_task_status_matches_short_id_only(tmp_path):  # REQ-38
    f = _make_index(tmp_path)

    # passing just "TASK-0002" (no slug) must still find the row
    assert update_task_status(str(tmp_path), "TASK-0002", "done") is True
    assert "| done          |" in _row_for(f, "TASK-0002")


def test_update_task_status_can_flip_to_action_needed(tmp_path):  # REQ-38
    f = _make_index(tmp_path)

    assert update_task_status(str(tmp_path), "TASK-0001-build", "action needed") is True
    assert "| action needed |" in _row_for(f, "TASK-0001")


def test_update_task_status_preserves_column_alignment(tmp_path):  # REQ-38
    f = _make_index(tmp_path)

    # Every transition should preserve the pipe positions of the row.
    baseline_pipes = [i for i, c in enumerate(_row_for(f, "TASK-0001")) if c == "|"]
    for target in ("in progress", "done", "action needed", "pending"):
        update_task_status(str(tmp_path), "TASK-0001-build", target)
        pipes = [i for i, c in enumerate(_row_for(f, "TASK-0001")) if c == "|"]
        assert pipes == baseline_pipes, f"pipes shifted after writing {target!r}"


def test_update_task_status_missing_file_returns_false(tmp_path):  # REQ-38
    # no index.md created
    assert update_task_status(str(tmp_path), "TASK-0001-build", "done") is False


def test_update_task_status_unmatched_id_returns_false(tmp_path):  # REQ-38
    _make_index(tmp_path)
    assert update_task_status(str(tmp_path), "TASK-9999-nope", "done") is False


def test_update_task_status_rejects_invalid_status(tmp_path):  # REQ-38
    _make_index(tmp_path)
    with pytest.raises(ValueError):
        update_task_status(str(tmp_path), "TASK-0001-build", "wip")


def test_update_task_status_flips_bug_status_with_slug(tmp_path):  # REQ-38
    """B-prefixed IDs are handled symmetrically with T-prefixed IDs (slug variant)."""
    f = _make_index(tmp_path)

    assert update_task_status(str(tmp_path), "BUG-0003-something", "done") is True

    row = _row_for(f, "BUG-0003")
    assert "done" in row
    assert row.count("|") == 6
    assert "| done          |" in row
    # sibling T rows untouched
    assert "| TASK-0001 | E1   | task | Build and dependencies | pending       |" in f.read_text(encoding="utf-8")


def test_update_task_status_matches_bare_bug_id(tmp_path):  # REQ-38
    """Bare B-IDs (no slug suffix) resolve to their row."""
    f = _make_index(tmp_path)

    assert update_task_status(str(tmp_path), "BUG-0003", "action needed") is True
    assert "| action needed |" in _row_for(f, "BUG-0003")


def test_update_task_status_widens_narrow_status_header(tmp_path):  # item-030 #5
    """A hand-written index.md with a Status header narrower than the
    canonical width gets auto-widened on the first status write, so the
    padded row doesn't visually break the table."""
    narrow_index = (
        "# Work Items\n"
        "\n"
        "| ID  | Epic | Type | Title    | Status  |\n"
        "|-----|------|------|----------|---------|\n"
        "| TASK-0001 | E1   | task | greet    | pending |\n"
    )
    f = _make_index(tmp_path, body=narrow_index)

    assert update_task_status(str(tmp_path), "TASK-0001", "in progress") is True

    text = f.read_text(encoding="utf-8")
    # Header cell widened to 15 chars (1 leading + 13 + 1 trailing)
    assert "| Status        |" in text
    # Separator cell widened to matching 15 dashes
    assert "|---------------|" in text
    # Data row's status also padded to 15-char cell content
    assert "| in progress   |" in text


def test_update_task_status_leaves_already_wide_header_alone(tmp_path):  # item-030 #5
    """Widen-only: an already-canonical header must not be resized."""
    f = _make_index(tmp_path)  # INDEX_SAMPLE already uses the canonical width
    before = f.read_text(encoding="utf-8")

    update_task_status(str(tmp_path), "TASK-0001-build", "done")

    text = f.read_text(encoding="utf-8")
    # Header line is unchanged.
    header_line_before = next(l for l in before.splitlines() if "| Status" in l)
    header_line_after  = next(l for l in text.splitlines()   if "| Status" in l)
    assert header_line_before == header_line_after
