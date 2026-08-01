"""Test-suite fixtures.

Autouse fixture that stubs ``orchestrator.tasks.find_test_docs_for_task``
to return a non-empty list — needed because ``critic_loop`` (per
REQ-0008 introduced by Epic E5) refuses any task whose ID has no
matching ``docs/tests/TEST-*.md`` file. Most legacy critic_loop tests
run against a fake ``/project`` dir with no real TEST files; without
this stub, every one of them would trip the coverage-gap refusal and
fail before exercising the behaviour under test.

Tests that specifically want to verify the coverage-gap-refusal path
opt out via ``@pytest.mark.no_test_docs_stub`` (or simply patch
``orchestrator.tasks.find_test_docs_for_task`` themselves inside the
test to return ``[]``).
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "no_test_docs_stub: opt this test out of the autouse "
        "find_test_docs_for_task stub (so the test can exercise the "
        "coverage-gap-refusal path directly)",
    )
    config.addinivalue_line(
        "markers",
        "needs_test_docs_stub: opt this test IN to the autouse "
        "find_test_docs_for_task stub (only tests in test_loops.py "
        "get it by default; anywhere else must opt in explicitly)",
    )


@pytest.fixture(autouse=True)
def _stub_find_test_docs_for_task(request: pytest.FixtureRequest, tmp_path: Path):
    """Make ``find_test_docs_for_task`` return a plausible non-empty list.

    Only applies to tests in ``test_loops.py`` (and any other future
    module that adds ``@pytest.mark.needs_test_docs_stub``) — this stub
    would corrupt tests that specifically exercise
    ``find_test_docs_for_task`` itself (``test_tasks.py``), so those
    modules opt out by default. Tests that want to exercise the
    coverage-gap-refusal path opt out per-test via
    ``@pytest.mark.no_test_docs_stub``.
    """
    if request.node.get_closest_marker("no_test_docs_stub"):
        yield
        return

    # Only stub for test_loops.py (and any module that explicitly opts in
    # via @pytest.mark.needs_test_docs_stub). Everything else runs without
    # the stub so it can call the real find_test_docs_for_task freely.
    module_name = request.node.module.__name__ if hasattr(request.node, "module") else ""
    opt_in = request.node.get_closest_marker("needs_test_docs_stub")
    # Compare on the leaf module name (last dot-separated segment) so this
    # works whether tests load as `orchestrator.tests.test_loops` (legacy
    # nested layout) or plain `test_loops` (current flat orchestrator-tests/
    # on pytest pythonpath).
    leaf = module_name.rsplit(".", 1)[-1]
    if not opt_in and leaf != "test_loops":
        yield
        return

    stub = tmp_path / "TEST-STUB.md"
    stub.write_text(
        "# TEST-STUB — autouse fixture placeholder\n\n"
        "**Epic:** none\n"
        "**Mode:** structural\n"
        "**REQ:** REQ-STUB\n"
        "**Task:** TASK-STUB\n\n"
        "## Assertion\nfixture placeholder — real coverage lives in "
        "individual tests.\n",
        encoding="utf-8",
    )
    # Also stub write_tests_phase — the legacy tests were written when
    # critic_loop skipped it entirely if test_doc_content was None. Under
    # the new per-task-discovery flow, write_tests_phase always runs (it
    # invokes runner.detect_task_test_files which shells out to git and
    # fails on the fake /project paths used by many tests). Stub it to
    # return (test_cmd, True) so control passes through to the actual
    # behaviour each test wants to exercise.
    with patch("orchestrator.tasks.find_test_docs_for_task", return_value=[stub]), \
         patch("orchestrator.loops.write_tests_phase", side_effect=lambda task, cmd, content, pd: (cmd, True)):
        yield
