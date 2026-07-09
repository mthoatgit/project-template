"""Tests for orchestrator.runner — test-runner subprocess (REQ-26), failure-count
heuristic (REQ-05..07), and language-agnostic test-file detection (REQ-31)."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from orchestrator import (
    _looks_like_test_file,
    detect_task_test_files,
    extract_failure_count,
    run_tests,
)

from orchestrator.tests.helpers import _mock_popen


# ─────────────────────────────────────────────────────────────
#  REQ-05  pytest format
#  REQ-06  Maven / Gradle format
#  REQ-07  unknown format → None
# ─────────────────────────────────────────────────────────────

@pytest.mark.parametrize("output, expected", [
    # REQ-05 — pytest
    ("1 failed, 2 passed in 0.5s",                          1),
    ("3 failed, 1 error, 2 passed in 1.2s",                 4),  # failures + errors summed
    ("2 errors in 0.3s",                                    2),  # errors only (plural)
    ("5 passed in 0.1s",                                    None),  # no failures → unparseable
    ("setup output\n3 failed, 1 passed in 1.0s\nfooter",   3),  # survives surrounding noise

    # REQ-06 — Maven / Gradle
    ("Tests run: 10, Failures: 2, Errors: 1, Skipped: 0",  3),
    ("Tests run: 5, Failures: 0, Errors: 0, Skipped: 0",   0),
    ("BUILD FAILURE\nTests run: 3, Failures: 3, Errors: 0", 3),

    # REQ-07 — unknown format
    ("Compilation failed: cannot find symbol",              None),
    ("",                                                    None),
    ("Process finished with exit code 1",                   None),
])
def test_extract_failure_count(output, expected):  # REQ-05, REQ-06, REQ-07
    assert extract_failure_count(output) == expected


# ─────────────────────────────────────────────────────────────
#  REQ-26  run_tests uses PowerShell on Windows, system shell elsewhere
# ─────────────────────────────────────────────────────────────

@patch("orchestrator.subprocess.Popen")
@patch("orchestrator.platform.system")
def test_run_tests_uses_powershell_on_windows(mock_system, mock_popen):  # REQ-26
    mock_system.return_value = "Windows"
    mock_popen.return_value = _mock_popen(returncode=0, output="1 passed\n")

    run_tests("pytest", "/project")

    call_args = mock_popen.call_args
    assert call_args[0][0] == ["powershell", "-NoProfile", "-Command", "pytest"]
    assert call_args[1].get("shell") is False


@patch("orchestrator.subprocess.Popen")
@patch("orchestrator.platform.system")
def test_run_tests_uses_shell_on_linux(mock_system, mock_popen):  # REQ-26
    mock_system.return_value = "Linux"
    mock_popen.return_value = _mock_popen(returncode=0, output="1 passed\n")

    run_tests("pytest", "/project")

    call_args = mock_popen.call_args
    assert call_args[0][0] == "pytest"
    assert call_args[1].get("shell") is True


# ─────────────────────────────────────────────────────────────
#  REQ-31  detect_task_test_files: finds new and modified test files
# ─────────────────────────────────────────────────────────────

@patch("orchestrator.subprocess.run")
def test_detect_task_test_files_returns_new_and_modified(mock_run):  # REQ-31
    mock_run.side_effect = [
        MagicMock(stdout="tests/test_config.py\nsrc/config.py\n"),   # git diff
        MagicMock(stdout="tests/test_new.py\n"),                      # git ls-files
    ]

    result = detect_task_test_files("/project")

    assert "tests/test_config.py" in result
    assert "tests/test_new.py" in result
    assert "src/config.py" not in result   # source files excluded


@patch("orchestrator.subprocess.run")
def test_detect_task_test_files_returns_empty_when_none(mock_run):  # REQ-31
    mock_run.side_effect = [
        MagicMock(stdout="src/config.py\n"),
        MagicMock(stdout=""),
    ]

    result = detect_task_test_files("/project")

    assert result == []


def test_detect_task_test_files_returns_dart_and_python(monkeypatch, tmp_path):  # REQ-31
    """End-to-end via detect_task_test_files: mix of Python + Dart + noise."""
    import orchestrator

    def fake_run(cmd, **kwargs):
        if cmd[:3] == ["git", "diff", "--name-only"]:
            return MagicMock(stdout="backend/tests/test_config.py\nsrc/config.py\n")
        if cmd[:3] == ["git", "ls-files", "--others"]:
            return MagicMock(stdout="frontend/test/widget_test.dart\n")
        return MagicMock(stdout="")
    monkeypatch.setattr(orchestrator.subprocess, "run", fake_run)

    result = detect_task_test_files(str(tmp_path))

    assert "backend/tests/test_config.py" in result
    assert "frontend/test/widget_test.dart" in result
    assert "src/config.py" not in result


# ─────────────────────────────────────────────────────────────
#  REQ-31  _looks_like_test_file: language-agnostic detection
# ─────────────────────────────────────────────────────────────

@pytest.mark.parametrize("path", [
    "backend/tests/test_health.py",              # pytest — test_X.py under tests/
    "backend/test_module.py",                    # pytest — test_X.py at any depth
    "src/module_test.py",                        # pytest — X_test.py convention
    "frontend/test/widget_test.dart",            # Flutter — X_test.dart under test/
    "lib/service/service_test.dart",             # Flutter — X_test.dart anywhere
    "pkg/module_test.go",                        # Go — X_test.go
    "src/lib/mod_test.rs",                       # Rust — X_test.rs
    "src/main/java/com/x/FooTest.java",          # JUnit — XTest.java
    "src/main/kotlin/com/x/FooTest.kt",          # JUnit / Kotest
    "src/Foo.Tests.cs",                          # NUnit — X.Tests.cs
    "web/components/button.test.tsx",            # Jest — X.test.tsx
    "web/services/api.spec.ts",                  # Jasmine / Angular — X.spec.ts
    "app/__tests__/user.js",                     # Jest __tests__ dir
    "spec/models/user_spec.rb",                  # RSpec — spec/ dir
])
def test_looks_like_test_file_true(path):  # REQ-31
    assert _looks_like_test_file(path) is True, f"expected {path} to be a test file"


@pytest.mark.parametrize("path", [
    "backend/src/main.py",                       # source
    "backend/src/config.py",                     # source
    "frontend/lib/main.dart",                    # Flutter entry
    "frontend/lib/models/task.dart",             # Flutter model
    "docs/tests/epics/E1-foundation.md",         # docs — not source
    "src/testing_utils.py",                      # helper, not a test
    "README.md",
])
def test_looks_like_test_file_false(path):  # REQ-31
    assert _looks_like_test_file(path) is False, f"expected {path} to NOT be a test file"
