"""Test-runner subprocess (REQ-26, REQ-32, REQ-34, REQ-35, REQ-36),
failure-count heuristic (REQ-05..07), and language-agnostic test-file
detection (REQ-31)."""
import os
import platform
import re
import subprocess
import sys


def run_tests(test_cmd: str, project_dir: str) -> tuple[bool, str]:
    """Run the configured test command and return ``(passed, output)``.

    On Windows: executed via PowerShell so that PowerShell syntax and
    PATH resolution work as expected (REQ-26).
    On other platforms: executed via the system shell.

    ``python`` at the start of the command is always replaced with the
    interpreter that is running the orchestrator (``sys.executable``) so
    that Windows App-Execution-Alias stubs cannot intercept the call
    (REQ-35).

    ``PYTHONUNBUFFERED=1`` is injected into the subprocess environment so
    that pytest and any Python-based test runner flush their output
    immediately. Output is streamed line-by-line so the log file updates
    in real time.
    """
    resolved = re.sub(r"^python3?\b", sys.executable.replace("\\", "/"), test_cmd)
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"

    if platform.system() == "Windows":
        cmd = ["powershell", "-NoProfile", "-Command", resolved]
        use_shell = False
    else:
        cmd = resolved
        use_shell = True

    proc = subprocess.Popen(
        cmd,
        shell=use_shell,
        cwd=project_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    lines: list[str] = []
    for raw_line in proc.stdout:
        sys.stdout.write(f"  │ {raw_line}")
        lines.append(raw_line)
    proc.wait()
    output = "".join(lines).strip()
    return proc.returncode == 0, output


def extract_failure_count(output: str) -> int | None:
    """Extract the total number of failing tests from runner output.

    Used by the Ralph Loop to detect whether Claude is making progress
    (fewer failures each round) or is stuck (same count repeating).
    Returns ``None`` when the format is not recognised — callers must
    handle this gracefully by skipping count-based checks.
    """
    # pytest: "3 failed", "2 errors" (summary line)
    pytest_fail = re.search(r'\b(\d+)\s+failed\b',  output)
    pytest_err  = re.search(r'\b(\d+)\s+errors?\b', output)
    if pytest_fail or pytest_err:
        return (int(pytest_fail.group(1)) if pytest_fail else 0) + \
               (int(pytest_err.group(1))  if pytest_err  else 0)

    # Maven / Gradle: "Failures: 3, Errors: 1"
    mvn_fail = re.search(r'[Ff]ailures?:\s*(\d+)', output)
    mvn_err  = re.search(r'[Ee]rrors?:\s*(\d+)',   output)
    if mvn_fail or mvn_err:
        return (int(mvn_fail.group(1)) if mvn_fail else 0) + \
               (int(mvn_err.group(1))  if mvn_err  else 0)

    return None


# ── Language-agnostic test-file detection (REQ-31) ─────────────
# A path counts as a test file if it has a source-code extension AND either
# lives under a well-known test directory OR its base name matches a common
# test-file naming convention. The extension gate keeps docs/tests/*.md and
# similar noise out. Together these cover pytest, Flutter/Dart, Go, Rust,
# JUnit / Kotest, NUnit, Jest / Jasmine, RSpec, and most other ecosystems.
_SOURCE_EXTENSIONS = frozenset({
    "py", "dart", "go", "rs", "java", "kt", "kts", "scala", "cs", "swift",
    "ts", "tsx", "js", "jsx", "mts", "cts", "mjs", "cjs",
    "rb", "php", "clj", "cljs", "ex", "exs", "elm",
})

_TEST_PATH_PATTERNS = [
    re.compile(r"(?:^|/)(?:tests?|specs?|__tests__)/", re.IGNORECASE),
    re.compile(r"/test_[^/]+\.\w+$", re.IGNORECASE),          # test_X.<ext>
    re.compile(r"_test\.\w+$", re.IGNORECASE),                # X_test.<ext>
    re.compile(r"Test\.[A-Za-z0-9]+$"),                       # XTest.<ext>   (case-sensitive)
    re.compile(r"Tests\.[A-Za-z0-9]+$"),                      # XTests.<ext>  (case-sensitive)
    re.compile(r"\.(?:test|spec)\.\w+$", re.IGNORECASE),      # X.test.<ext>, X.spec.<ext>
]


def _looks_like_test_file(path: str) -> bool:
    """Heuristic used by ``detect_task_test_files``. Path separators normalised
    to ``/`` before matching so the same patterns cover Windows and Unix.
    Non-code file extensions (`.md`, `.txt`, ...) are rejected up front so
    that documentation about tests (e.g. ``docs/tests/*.md``) is not
    misclassified."""
    p = path.replace("\\", "/")
    ext = p.rsplit(".", 1)[-1].lower() if "." in p.rsplit("/", 1)[-1] else ""
    if ext not in _SOURCE_EXTENSIONS:
        return False
    return any(pat.search(p) for pat in _TEST_PATH_PATTERNS)


def detect_task_test_files(project_dir: str) -> list[str]:
    """Return test files added or modified since the last commit (REQ-31).

    Language-agnostic: any path recognised by ``_looks_like_test_file``
    across the ``git diff`` set plus the ``untracked`` set is returned.
    """
    modified = subprocess.run(
        ["git", "diff", "--name-only"],
        cwd=project_dir, capture_output=True, text=True, encoding="utf-8",
    ).stdout.splitlines()

    untracked = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"],
        cwd=project_dir, capture_output=True, text=True, encoding="utf-8",
    ).stdout.splitlines()

    return [f for f in modified + untracked if _looks_like_test_file(f)]
