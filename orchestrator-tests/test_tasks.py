"""Tests for orchestrator.tasks — load_tasks + find_test_docs_for_task.

Covers item 003 (Epic E5) test specs:
- TEST-0008 — load_tasks recognizes both TASK-*.md and BUG-*.md files
- TEST-0009 — find_test_docs_for_task returns exactly matching TEST files
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from orchestrator import find_test_docs_for_task, load_tasks


# ─── load_tasks basics ─────────────────────────────────────────────


def test_load_tasks_directory_returns_md_files_only(tmp_path: Path) -> None:
    (tmp_path / "TASK-0001-foo.md").write_text("content foo", encoding="utf-8")
    (tmp_path / "TASK-0002-bar.md").write_text("content bar", encoding="utf-8")
    (tmp_path / "not_a_task.txt").write_text("skip me", encoding="utf-8")

    tasks = load_tasks(str(tmp_path))

    ids = [t["id"] for t in tasks]
    assert len(tasks) == 2
    assert "TASK-0001-foo" in ids
    assert "TASK-0002-bar" in ids


def test_load_tasks_skips_templates(tmp_path: Path) -> None:
    (tmp_path / "TASK-0001-real.md").write_text("real content", encoding="utf-8")
    (tmp_path / "_TEMPLATE_TASK.md").write_text("template — should be skipped", encoding="utf-8")
    (tmp_path / "_TEMPLATE_BUG.md").write_text("template — should be skipped", encoding="utf-8")

    tasks = load_tasks(str(tmp_path))

    assert len(tasks) == 1
    assert tasks[0]["id"] == "TASK-0001-real"


def test_load_tasks_skips_index_and_readme(tmp_path: Path) -> None:
    """Scaffolding files (index.md, README.md) are NOT work items — REQ-0006."""
    (tmp_path / "TASK-0001-real.md").write_text("real content", encoding="utf-8")
    (tmp_path / "index.md").write_text("| ID | Title | Status |", encoding="utf-8")
    (tmp_path / "README.md").write_text("Work Items orientation", encoding="utf-8")

    tasks = load_tasks(str(tmp_path))

    assert len(tasks) == 1
    assert tasks[0]["id"] == "TASK-0001-real"


def test_load_tasks_returns_files_sorted(tmp_path: Path) -> None:
    (tmp_path / "TASK-0003-last.md").write_text("c", encoding="utf-8")
    (tmp_path / "TASK-0001-first.md").write_text("a", encoding="utf-8")
    (tmp_path / "TASK-0002-middle.md").write_text("b", encoding="utf-8")

    tasks = load_tasks(str(tmp_path))

    assert [t["id"] for t in tasks] == ["TASK-0001-first", "TASK-0002-middle", "TASK-0003-last"]


def test_load_tasks_single_file(tmp_path: Path) -> None:
    f = tmp_path / "TASK-0005-solo-task.md"
    f.write_text("single-task content", encoding="utf-8")

    tasks = load_tasks(str(f))

    assert len(tasks) == 1
    assert tasks[0]["id"] == "TASK-0005-solo-task"


def test_load_tasks_json_list(tmp_path: Path) -> None:
    f = tmp_path / "tasks.json"
    f.write_text(json.dumps([
        {"id": "TASK-0001", "content": "first"},
        {"id": "TASK-0002", "content": "second"},
    ]), encoding="utf-8")

    tasks = load_tasks(str(f))

    assert len(tasks) == 2
    assert tasks[0]["id"] == "TASK-0001"


# ─── TEST-0008: TASK + BUG both loaded ─────────────────────────────


def test_load_tasks_recognizes_both_TASK_and_BUG_files(tmp_path: Path) -> None:
    """TEST-0008 — flat docs/tasks/ contains both TASK-*.md and BUG-*.md; both are work items."""
    (tmp_path / "TASK-0001-implement-feature.md").write_text("task content", encoding="utf-8")
    (tmp_path / "BUG-0002-fix-crash.md").write_text("bug content", encoding="utf-8")
    (tmp_path / "TASK-0003-another-task.md").write_text("task content", encoding="utf-8")
    (tmp_path / "_TEMPLATE_TASK.md").write_text("scaffolding", encoding="utf-8")
    (tmp_path / "_TEMPLATE_BUG.md").write_text("scaffolding", encoding="utf-8")
    (tmp_path / "README.md").write_text("scaffolding", encoding="utf-8")
    (tmp_path / "index.md").write_text("scaffolding", encoding="utf-8")

    tasks = load_tasks(str(tmp_path))
    ids = {t["id"] for t in tasks}

    assert ids == {"TASK-0001-implement-feature", "BUG-0002-fix-crash", "TASK-0003-another-task"}
    # Scaffolding MUST NOT appear
    assert "_TEMPLATE_TASK" not in ids
    assert "_TEMPLATE_BUG" not in ids
    assert "README" not in ids
    assert "index" not in ids


# ─── find_test_docs_for_task ───────────────────────────────────────


def _make_test_file(dir: Path, name: str, task_header_value: str) -> Path:
    """Write a minimal TEST-*.md fixture with a **Task:** header line."""
    f = dir / name
    f.write_text(
        f"# {name.replace('.md', '')}\n"
        f"\n"
        f"**Epic:** E5-test\n"
        f"**Mode:** structural\n"
        f"**REQ:** REQ-0001\n"
        f"**Task:** {task_header_value}\n"
        f"\n"
        f"## Assertion\n"
        f"something MUST hold.\n",
        encoding="utf-8",
    )
    return f


def test_find_test_docs_for_task_returns_matching_files(tmp_path: Path) -> None:
    """TEST-0009 — for task-ID X, return exactly TEST files whose **Task:** header contains X."""
    tests_dir = tmp_path / "docs" / "tests"
    tests_dir.mkdir(parents=True)

    ta = _make_test_file(tests_dir, "TEST-0001-alpha.md", "TASK-0001")
    tb = _make_test_file(tests_dir, "TEST-0002-beta.md", "TASK-0001")
    _make_test_file(tests_dir, "TEST-0003-gamma.md", "TASK-0002")  # unrelated task
    td = _make_test_file(tests_dir, "TEST-0004-delta.md", "TASK-0001, TASK-0003")  # multi-task, includes ours

    task = {"id": "TASK-0001-my-slug", "content": "...", "path": "irrelevant"}
    result = find_test_docs_for_task(task, str(tmp_path))

    assert set(result) == {ta, tb, td}


def test_find_test_docs_for_task_returns_empty_when_no_matches(tmp_path: Path) -> None:
    """TEST-0010 (partial) — zero-match case returns empty list (caller decides refusal)."""
    tests_dir = tmp_path / "docs" / "tests"
    tests_dir.mkdir(parents=True)
    _make_test_file(tests_dir, "TEST-0001-alpha.md", "TASK-0999")  # no match

    task = {"id": "TASK-0001-my-slug", "content": "...", "path": "irrelevant"}
    result = find_test_docs_for_task(task, str(tmp_path))

    assert result == []


def test_find_test_docs_for_task_handles_missing_tests_dir(tmp_path: Path) -> None:
    """When docs/tests/ does not exist, return empty list (caller refuses)."""
    task = {"id": "TASK-0001-my-slug", "content": "...", "path": "irrelevant"}
    result = find_test_docs_for_task(task, str(tmp_path))

    assert result == []


def test_find_test_docs_for_task_handles_bug_ids(tmp_path: Path) -> None:
    """BUG-<NNNN> IDs work the same way as TASK-<NNNN>."""
    tests_dir = tmp_path / "docs" / "tests"
    tests_dir.mkdir(parents=True)
    tb = _make_test_file(tests_dir, "TEST-0007-bug-regression.md", "BUG-0042")

    task = {"id": "BUG-0042-fix-crash", "content": "...", "path": "irrelevant"}
    result = find_test_docs_for_task(task, str(tmp_path))

    assert result == [tb]


def test_find_test_docs_for_task_task_id_boundary(tmp_path: Path) -> None:
    """Word boundary at end prevents TASK-00010 matching a search for TASK-0001.

    Under the 4-digit convention TASK-00010 is impossible, but the \\b in
    the regex is cheap defence in depth. Verifies we don't false-positive
    on prefix substrings.
    """
    tests_dir = tmp_path / "docs" / "tests"
    tests_dir.mkdir(parents=True)
    _make_test_file(tests_dir, "TEST-0001-different.md", "TASK-00019")  # hypothetical 5-digit; must NOT match

    task = {"id": "TASK-0001-my-slug", "content": "...", "path": "irrelevant"}
    result = find_test_docs_for_task(task, str(tmp_path))

    assert result == []


def test_find_test_docs_for_task_ignores_prose_task_mentions(tmp_path: Path) -> None:
    """Only ^**Task:** header lines count — prose mentions of task IDs elsewhere in a TEST file must not match."""
    tests_dir = tmp_path / "docs" / "tests"
    tests_dir.mkdir(parents=True)
    f = tests_dir / "TEST-0001-mention-only.md"
    f.write_text(
        "# TEST-0001\n"
        "\n"
        "**Epic:** E5\n"
        "**Mode:** structural\n"
        "**REQ:** REQ-0001\n"
        "**Task:** TASK-0999\n"  # actual header — does NOT match TASK-0001
        "\n"
        "## Notes\n"
        "Historical: this test replaces the one written for TASK-0001 originally.\n",  # prose mention
        encoding="utf-8",
    )

    task = {"id": "TASK-0001-my-slug", "content": "...", "path": "irrelevant"}
    result = find_test_docs_for_task(task, str(tmp_path))

    assert result == []  # prose mention MUST NOT trigger a match
