"""Tests for orchestrator.tasks — task loading (REQ-01..04) and
test-design-doc discovery (REQ-29)."""
from __future__ import annotations

import json

import pytest

from orchestrator import find_test_doc, load_tasks


# ─────────────────────────────────────────────────────────────
#  REQ-01  directory of .md files — all loaded, _TEMPLATE skipped
#  REQ-02  single .md file
#  REQ-03  .json file
#  REQ-04  .yaml / .yml file
# ─────────────────────────────────────────────────────────────

def test_load_tasks_from_directory(tmp_path):  # REQ-01
    (tmp_path / "T01-foo.md").write_text("content foo", encoding="utf-8")
    (tmp_path / "T02-bar.md").write_text("content bar", encoding="utf-8")

    tasks = load_tasks(str(tmp_path))

    assert len(tasks) == 2
    ids = [t["id"] for t in tasks]
    assert "T01-foo" in ids
    assert "T02-bar" in ids


def test_load_tasks_from_directory_skips_template(tmp_path):  # REQ-01
    (tmp_path / "T01-real.md").write_text("real content", encoding="utf-8")
    (tmp_path / "_TEMPLATE.md").write_text("template content", encoding="utf-8")

    tasks = load_tasks(str(tmp_path))

    assert len(tasks) == 1
    assert tasks[0]["id"] == "T01-real"


def test_load_tasks_from_directory_sorted(tmp_path):  # REQ-01
    (tmp_path / "T03-last.md").write_text("c", encoding="utf-8")
    (tmp_path / "T01-first.md").write_text("a", encoding="utf-8")
    (tmp_path / "T02-middle.md").write_text("b", encoding="utf-8")

    tasks = load_tasks(str(tmp_path))

    assert [t["id"] for t in tasks] == ["T01-first", "T02-middle", "T03-last"]


def test_load_tasks_from_single_md_file(tmp_path):  # REQ-02
    f = tmp_path / "T05-task.md"
    f.write_text("# My Task\nDo something.", encoding="utf-8")

    tasks = load_tasks(str(f))

    assert len(tasks) == 1
    assert tasks[0]["id"] == "T05-task"
    assert "Do something." in tasks[0]["content"]


def test_load_tasks_from_json_list(tmp_path):  # REQ-03
    data = [
        {"id": "T01", "content": "first"},
        {"id": "T02", "content": "second"},
    ]
    f = tmp_path / "tasks.json"
    f.write_text(json.dumps(data), encoding="utf-8")

    tasks = load_tasks(str(f))

    assert len(tasks) == 2
    assert tasks[0]["id"] == "T01"
    assert tasks[1]["content"] == "second"


def test_load_tasks_from_json_single_object(tmp_path):  # REQ-03
    data = {"id": "T01", "content": "only task"}
    f = tmp_path / "tasks.json"
    f.write_text(json.dumps(data), encoding="utf-8")

    tasks = load_tasks(str(f))

    assert len(tasks) == 1
    assert tasks[0]["id"] == "T01"


def test_load_tasks_from_yaml(tmp_path):  # REQ-04
    yaml = pytest.importorskip("yaml")
    data = [{"id": "T01", "content": "yaml task"}]
    f = tmp_path / "tasks.yaml"
    f.write_text(yaml.dump(data), encoding="utf-8")

    tasks = load_tasks(str(f))

    assert len(tasks) == 1
    assert tasks[0]["id"] == "T01"
    assert tasks[0]["content"] == "yaml task"


def test_load_tasks_from_yml_extension(tmp_path):  # REQ-04
    yaml = pytest.importorskip("yaml")
    data = [{"id": "T02", "content": "yml task"}]
    f = tmp_path / "tasks.yml"
    f.write_text(yaml.dump(data), encoding="utf-8")

    tasks = load_tasks(str(f))

    assert len(tasks) == 1
    assert tasks[0]["id"] == "T02"


# ─────────────────────────────────────────────────────────────
#  REQ-29  find_test_doc: locate and validate Epic test design doc
# ─────────────────────────────────────────────────────────────

def test_find_test_doc_returns_path_when_found(tmp_path):  # REQ-29
    doc = tmp_path / "docs" / "tests" / "epics"
    doc.mkdir(parents=True)
    (doc / "E1-tests.md").write_text("# Test Design\nsome scenarios", encoding="utf-8")

    result = find_test_doc("docs/tasks/epics/E1/", str(tmp_path))

    assert result.name == "E1-tests.md"


def test_find_test_doc_exits_when_missing(tmp_path):  # REQ-29
    (tmp_path / "docs" / "tests" / "epics").mkdir(parents=True)

    with pytest.raises(SystemExit):
        find_test_doc("docs/tasks/epics/E1/", str(tmp_path))


def test_find_test_doc_exits_when_template(tmp_path):  # REQ-29
    doc_dir = tmp_path / "docs" / "tests" / "epics"
    doc_dir.mkdir(parents=True)
    (doc_dir / "E1-tests.md").write_text(
        "---\nstatus: template\n---\n# Test Design", encoding="utf-8"
    )

    with pytest.raises(SystemExit):
        find_test_doc("docs/tasks/epics/E1/", str(tmp_path))


def test_find_test_doc_exits_when_no_epic_in_path(tmp_path):  # REQ-29
    with pytest.raises(SystemExit):
        find_test_doc(str(tmp_path / "some" / "flat" / "tasks.json"), str(tmp_path))
