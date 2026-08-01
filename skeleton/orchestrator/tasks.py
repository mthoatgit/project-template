"""Task loading (REQ-01..04) and per-task test-spec discovery (REQ-0008).

Per-task test discovery replaced the retired Epic-level ``find_test_doc``
after Epic E5 (Orchestrator flat-layout support) synced project-template
to the REQ-0006 flat task-file convention and the three-mode
verification model. Machines MUST read test-spec metadata from the
TEST-*.md file headers directly (see workflow-tests "Machine
discovery" section) — NOT from docs/tests/index.md, which is a
human aggregation.
"""
import json
import re
import sys
from pathlib import Path


TASK_ID_RE = re.compile(r"^(TASK|BUG)-\d{4}")


def load_tasks(tasks_path: str) -> list[dict]:
    path = Path(tasks_path)
    tasks: list[dict] = []

    if path.is_dir():
        for f in sorted(path.rglob("*.md")):
            if "_TEMPLATE" in f.name:
                continue
            # Skip index.md and README.md — scaffolding, not work items.
            if f.name in ("index.md", "README.md"):
                continue
            tasks.append({
                "id": f.stem,
                "content": f.read_text(encoding="utf-8"),
                "path": str(f),
            })
    elif path.suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        tasks = data if isinstance(data, list) else [data]
    elif path.suffix in (".yaml", ".yml"):
        try:
            import yaml
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            tasks = data if isinstance(data, list) else [data]
        except ImportError:
            print("[ERROR] PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
            sys.exit(1)
    else:
        tasks.append({
            "id": path.stem,
            "content": path.read_text(encoding="utf-8"),
            "path": str(path),
        })

    return tasks


def find_test_docs_for_task(task: dict, project_dir: str) -> list[Path]:
    """Discover TEST-*.md files whose **Task:** header contains this task's ID.

    Task-ID is extracted from the task filename stem via regex (TASK|BUG)-\\d{4}.
    Discovery scans docs/tests/TEST-*.md for the anchored header pattern
    ``^**Task:** .*<task-id>`` (regex on multiline content).

    Returns list of matching Path objects (sorted). Empty list = coverage gap;
    caller decides whether to refuse the task (see loops.critic_loop).
    Machines MUST NOT parse docs/tests/index.md — that file is a human
    aggregation, not the primary SoT for the mapping (per REQ-0008 and the
    Work-item anchoring section of docs/tests/strategy.md).
    """
    m = TASK_ID_RE.match(task["id"])
    if not m:
        return []
    task_id = m.group(0)

    tests_dir = Path(project_dir) / "docs" / "tests"
    if not tests_dir.is_dir():
        return []

    # \b (word boundary) at end guards against TASK-00010 matching a search for
    # TASK-0001 — impossible under the 4-digit convention but cheap defence.
    pattern = re.compile(
        rf"^\*\*Task:\*\* .*{re.escape(task_id)}\b",
        re.MULTILINE,
    )
    matches: list[Path] = []
    for f in sorted(tests_dir.glob("TEST-*.md")):
        try:
            content = f.read_text(encoding="utf-8")
        except OSError:
            continue
        if pattern.search(content):
            matches.append(f)
    return matches
