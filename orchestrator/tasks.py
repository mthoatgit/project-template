"""Task loading (REQ-01..04) and test-design-doc discovery (REQ-29)."""
import json
import re
import sys
from pathlib import Path


def load_tasks(tasks_path: str) -> list[dict]:
    path = Path(tasks_path)
    tasks: list[dict] = []

    if path.is_dir():
        for f in sorted(path.rglob("*.md")):
            if "_TEMPLATE" not in f.name:
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
        tasks = [{
            "id": path.stem,
            "content": path.read_text(encoding="utf-8"),
            "path": str(path),
        }]

    return tasks


def find_test_doc(tasks_path: str, project_dir: str) -> "Path":
    """Find and validate the Epic's test design doc (REQ-29). Exits if missing or template."""
    epic_id = None
    for part in Path(tasks_path).parts:
        if re.match(r"^E\d+", part, re.IGNORECASE):
            epic_id = part
            break

    if not epic_id:
        print(
            f"[ERROR] Cannot determine Epic ID from --tasks path: {tasks_path}\n"
            f"        Expected a path containing an Epic folder, e.g. docs/tasks/epics/E1/",
            file=sys.stderr,
        )
        sys.exit(1)

    test_docs_dir = Path(project_dir) / "docs" / "tests" / "epics"
    matches = sorted(test_docs_dir.glob(f"{epic_id}-*.md"))

    if not matches:
        print(
            f"[ERROR] Test design doc not found: docs/tests/epics/{epic_id}-*.md\n"
            f"        Complete Phase 4 (test design) before running the orchestrator.",
            file=sys.stderr,
        )
        sys.exit(1)

    doc = matches[0]
    content = doc.read_text(encoding="utf-8")
    if "status: template" in content[:300]:
        print(
            f"[ERROR] Test design doc is still a template: {doc.relative_to(project_dir)}\n"
            f"        Complete Phase 4 (test design) before running the orchestrator.",
            file=sys.stderr,
        )
        sys.exit(1)

    return doc
