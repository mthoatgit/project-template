"""Tests for orchestrator.loops — ralph_loop, critic_loop, write_tests_phase
(REQ-08..20, REQ-30/31 abort path, REQ-38 status flips)."""
from __future__ import annotations

from unittest.mock import patch

from orchestrator import (
    STUCK_STREAK_THRESHOLD,
    critic_loop,
    ralph_loop,
    write_tests_phase,
)

from helpers import TASK


# ─────────────────────────────────────────────────────────────
#  REQ-08  passes on first attempt
#  REQ-09  passes after fix attempt
# ─────────────────────────────────────────────────────────────

@patch("orchestrator.runner.run_tests")
@patch("orchestrator.claude.run_claude")
def test_passes_on_first_attempt(mock_claude, mock_tests):  # REQ-08
    mock_claude.return_value = (0, "implemented")
    mock_tests.return_value  = (True, "1 passed in 0.1s")

    assert ralph_loop(TASK, "pytest", "/project", max_iterations=5) is True
    assert mock_claude.call_count == 1
    assert mock_tests.call_count  == 1


@patch("orchestrator.runner.run_tests")
@patch("orchestrator.claude.run_claude")
def test_passes_after_one_retry(mock_claude, mock_tests):  # REQ-09
    mock_claude.return_value = (0, "fixed")
    mock_tests.side_effect   = [
        (False, "2 failed in 0.3s"),
        (True,  "2 passed in 0.3s"),
    ]

    assert ralph_loop(TASK, "pytest", "/project", max_iterations=5) is True
    assert mock_claude.call_count == 2
    assert mock_tests.call_count  == 2


# ─────────────────────────────────────────────────────────────
#  REQ-10  criterion 1 — identical output
# ─────────────────────────────────────────────────────────────

@patch("orchestrator.runner.run_tests")
@patch("orchestrator.claude.run_claude")
def test_exit_identical_output(mock_claude, mock_tests):  # REQ-10
    mock_claude.return_value = (0, "")
    mock_tests.return_value  = (False, "3 failed, AssertionError")

    assert ralph_loop(TASK, "pytest", "/project", max_iterations=5) is False
    assert mock_tests.call_count == 2  # iter 0 sets baseline, iter 1 matches → stop


# ─────────────────────────────────────────────────────────────
#  REQ-11  criterion 2 — stuck streak
#  REQ-12  criterion 2 — streak resets on progress
# ─────────────────────────────────────────────────────────────

@patch("orchestrator.runner.run_tests")
@patch("orchestrator.claude.run_claude")
def test_exit_stuck_streak(mock_claude, mock_tests):  # REQ-11
    mock_claude.return_value = (0, "tweaked code")
    mock_tests.side_effect = [
        (False, f"2 failed, attempt {i}, different message") for i in range(10)
    ]

    assert ralph_loop(TASK, "pytest", "/project", max_iterations=5) is False
    # iter 0: count=2, streak=0
    # iter 1: count=2, streak=1  (< threshold)
    # iter 2: count=2, streak=2  (>= threshold → stop)
    assert mock_tests.call_count == STUCK_STREAK_THRESHOLD + 1


@patch("orchestrator.runner.run_tests")
@patch("orchestrator.claude.run_claude")
def test_stuck_streak_resets_on_progress(mock_claude, mock_tests):  # REQ-12
    mock_claude.return_value = (0, "fixed")
    mock_tests.side_effect = [
        (False, "3 failed, attempt 0"),  # iter 0: count=3
        (False, "3 failed, attempt 1"),  # iter 1: count=3, streak=1
        (False, "2 failed, attempt 2"),  # iter 2: count=2, streak resets to 0
        (True,  "2 passed in 0.5s"),     # iter 3: pass
    ]

    assert ralph_loop(TASK, "pytest", "/project", max_iterations=5) is True
    assert mock_tests.call_count == 4


# ─────────────────────────────────────────────────────────────
#  REQ-13  criterion 3 — regression
# ─────────────────────────────────────────────────────────────

@patch("orchestrator.runner.run_tests")
@patch("orchestrator.claude.run_claude")
def test_exit_regression(mock_claude, mock_tests):  # REQ-13
    mock_claude.return_value = (0, "attempted fix")
    mock_tests.side_effect = [
        (False, "1 failed in 0.2s"),  # iter 0: 1 failure
        (False, "3 failed in 0.2s"),  # iter 1: regression to 3
    ]

    assert ralph_loop(TASK, "pytest", "/project", max_iterations=5) is False
    assert mock_tests.call_count == 2


# ─────────────────────────────────────────────────────────────
#  REQ-14  criterion 4 — max iterations
# ─────────────────────────────────────────────────────────────

@patch("orchestrator.runner.run_tests")
@patch("orchestrator.claude.run_claude")
def test_exit_max_iterations(mock_claude, mock_tests):  # REQ-14
    max_iter = 3
    mock_claude.return_value = (0, "incremental fix")
    mock_tests.side_effect = [
        (False, f"{10 - i} failed, iteration {i}") for i in range(max_iter + 1)
    ]

    assert ralph_loop(TASK, "pytest", "/project", max_iterations=max_iter) is False
    assert mock_tests.call_count == max_iter + 1


# ─────────────────────────────────────────────────────────────
#  Reusable Option-H gate responses (backlog item 028)
# ─────────────────────────────────────────────────────────────
#  Per happy-path design cycle: 4 Claude calls
#    (1) implement, (2) struktur_check, (3) docs_write, (4) final_approval
#  docs_write returns bare text = "ok" path (no JSON escape).

_STRUKTUR_PASS = (0, '{"pass": true, "reason": "structure sound"}')
_STRUKTUR_FAIL = (0, '{"pass": false, "reason": "wrong abstraction"}')
_DOCS_OK       = (0, "Updated README and CLAUDE.md.")
_DOCS_ESCAPE   = (0, '{"status": "design_issue", "reason": "leaky abstraction"}')
_FINAL_APPROVE = (0, '{"approve": true, "route_to": null, "criterion": null, "reason": "clean"}')
_FINAL_DOCS    = (0, '{"approve": false, "route_to": "docs", "criterion": "factual_error", "reason": "wrong version"}')
_FINAL_DESIGN  = (0, '{"approve": false, "route_to": "design", "criterion": "leaky_abstraction", "reason": "docs need impl details"}')


# ─────────────────────────────────────────────────────────────
#  REQ-15 (adapted for item 028): all four gates run after tests pass
# ─────────────────────────────────────────────────────────────

@patch("orchestrator.runner.run_tests")
@patch("orchestrator.claude.run_claude")
def test_all_four_gates_run_after_tests_pass(mock_claude, mock_tests):  # REQ-15 / item-028
    mock_claude.side_effect = [
        (0, "implemented"),  # Phase 1: implement
        _STRUKTUR_PASS,      # Phase 2: struktur_check
        _DOCS_OK,            # Phase 3: docs_write
        _FINAL_APPROVE,      # Phase 4: final_approval
    ]
    mock_tests.return_value = (True, "1 passed")

    result = critic_loop(TASK, "pytest", "/project", max_ralph_iterations=5, max_critic_iterations=3)

    assert result is True
    assert mock_claude.call_count == 4


# ─────────────────────────────────────────────────────────────
#  REQ-18 (adapted for item 028): final_approval route_to="design"
#                                 feeds feedback back into Ralph
# ─────────────────────────────────────────────────────────────

@patch("orchestrator.runner.run_tests")
@patch("orchestrator.claude.run_claude")
def test_final_approval_design_reject_triggers_reimplementation_with_feedback(mock_claude, mock_tests):  # REQ-18 / item-028
    mock_claude.side_effect = [
        # Cycle 1: implement → struktur pass → docs ok → final rejects (design)
        (0, "first implementation"),
        _STRUKTUR_PASS,
        _DOCS_OK,
        _FINAL_DESIGN,
        # Cycle 2: re-implement with feedback → all gates pass
        (0, "second implementation"),
        _STRUKTUR_PASS,
        _DOCS_OK,
        _FINAL_APPROVE,
    ]
    mock_tests.return_value = (True, "all passed")

    result = critic_loop(TASK, "pytest", "/project", max_ralph_iterations=5, max_critic_iterations=3)

    assert result is True
    # The re-implementation call (5th claude call = index 4) must include
    # the design-side feedback from the previous final_approval reject.
    reimpl_prompt = mock_claude.call_args_list[4][0][0]
    assert "leaky_abstraction" in reimpl_prompt or "docs need impl details" in reimpl_prompt


# ─────────────────────────────────────────────────────────────
#  REQ-19  critic stuck detection — same feedback twice
# ─────────────────────────────────────────────────────────────

@patch("orchestrator.runner.run_tests")
@patch("orchestrator.claude.run_claude")
def test_critic_loop_aborts_on_repeated_feedback(mock_claude, mock_tests):  # REQ-19 / item-028
    """Struktur-check rejecting with the same reason twice ⇒ stuck ⇒ abort."""
    mock_claude.side_effect = [
        (0, "implementation v1"),
        _STRUKTUR_FAIL,                 # cycle 1: struktur rejects
        (0, "implementation v2"),
        _STRUKTUR_FAIL,                 # cycle 2: same reason → stuck
    ]
    mock_tests.return_value = (True, "all passed")

    result = critic_loop(TASK, "pytest", "/project", max_ralph_iterations=5, max_critic_iterations=3)

    assert result is False
    assert mock_claude.call_count == 4


# ─────────────────────────────────────────────────────────────
#  REQ-20 (adapted for item 028): outer design-cycle ceiling
# ─────────────────────────────────────────────────────────────

@patch("orchestrator.runner.run_tests")
@patch("orchestrator.claude.run_claude")
def test_critic_loop_max_iterations(mock_claude, mock_tests):  # REQ-20 / item-028
    """Each design cycle: impl + struktur-fail (different reasons to avoid stuck).
    Cycles = max_critic + 1; struktur fails immediately so only 2 calls per cycle."""
    max_critic = 2
    responses = []
    for i in range(max_critic + 1):
        responses.append((0, f"impl {i}"))
        # Different reason per cycle keeps stuck-detection from firing early.
        responses.append((0, f'{{"pass": false, "reason": "concern {i}"}}'))
    mock_claude.side_effect = responses
    mock_tests.return_value = (True, "all passed")

    result = critic_loop(
        TASK, "pytest", "/project",
        max_ralph_iterations=5, max_critic_iterations=max_critic,
    )

    assert result is False
    assert mock_claude.call_count == (max_critic + 1) * 2


@patch("orchestrator.runner.run_tests")
@patch("orchestrator.claude.run_claude")
def test_critic_loop_fails_if_ralph_loop_fails(mock_claude, mock_tests):  # REQ-20
    mock_claude.return_value = (0, "")
    mock_tests.return_value = (False, "3 failed, identical every time")

    result = critic_loop(TASK, "pytest", "/project", max_ralph_iterations=5, max_critic_iterations=3)

    assert result is False


# ─────────────────────────────────────────────────────────────
#  REQ-25  task marked failed if retry with revert context still cannot fix
# ─────────────────────────────────────────────────────────────

@patch("orchestrator.runner.run_tests")
@patch("orchestrator.claude.run_claude")
def test_task_marked_failed_when_retry_cannot_fix(mock_claude, mock_tests):  # REQ-25
    mock_claude.return_value = (0, "")
    mock_tests.return_value = (False, "5 failed, tests still broken")

    result = critic_loop(
        TASK, "pytest", "/project",
        max_ralph_iterations=5, max_critic_iterations=3,
        revert_context="Previous commit caused 5 failures",
    )

    assert result is False


# ─────────────────────────────────────────────────────────────
#  REQ-31  write_tests_phase: fails task when no files created
# ─────────────────────────────────────────────────────────────

@patch("orchestrator.runner.detect_task_test_files", return_value=[])
@patch("orchestrator.claude.run_claude", return_value=(0, "wrote nothing"))
def test_write_tests_phase_fails_when_no_files_created(mock_claude, mock_detect):  # REQ-31
    cmd, ok = write_tests_phase(TASK, "pytest tests/", "# doc", "/project")

    assert ok is False
    assert cmd == "pytest tests/"  # original cmd returned unchanged


# ─────────────────────────────────────────────────────────────
#  REQ-38  critic_loop flips index.md status through the lifecycle
# ─────────────────────────────────────────────────────────────

@patch("orchestrator.status.update_task_status")
@patch("orchestrator.claude.run_claude")
@patch("orchestrator.runner.run_tests")
def test_critic_loop_flips_status_to_done_on_success(  # REQ-38 / item-028
    mock_tests, mock_claude, mock_update, tmp_path,
):
    mock_tests.return_value = (True, "pytest: 3 passed")
    mock_claude.side_effect = [
        (0, "implemented"), _STRUKTUR_PASS, _DOCS_OK, _FINAL_APPROVE,
    ]

    ok = critic_loop(TASK, "pytest", str(tmp_path), max_ralph_iterations=1, max_critic_iterations=1)

    assert ok is True
    calls = [c.args for c in mock_update.call_args_list]
    assert (str(tmp_path), TASK["id"], "in progress") in calls
    assert (str(tmp_path), TASK["id"], "done") in calls


@patch("orchestrator.status.update_task_status")
@patch("orchestrator.claude.run_claude")
@patch("orchestrator.runner.run_tests")
def test_critic_loop_flips_status_to_action_needed_on_failure(  # REQ-38
    mock_tests, mock_claude, mock_update, tmp_path,
):
    # tests never pass → ralph_loop returns False → critic_loop returns False
    mock_tests.return_value = (False, "pytest: 3 failed")
    mock_claude.return_value = (0, "")

    ok = critic_loop(TASK, "pytest", str(tmp_path), max_ralph_iterations=1, max_critic_iterations=1)

    assert ok is False
    calls = [c.args for c in mock_update.call_args_list]
    assert (str(tmp_path), TASK["id"], "in progress") in calls
    assert (str(tmp_path), TASK["id"], "action needed") in calls


# ═══════════════════════════════════════════════════════════════
#  Option-H DoD gates — phase-specific behaviors (backlog item 028)
# ═══════════════════════════════════════════════════════════════

@patch("orchestrator.runner.run_tests")
@patch("orchestrator.claude.run_claude")
def test_struktur_reject_routes_to_ralph_with_feedback(mock_claude, mock_tests):  # item-028
    """Struktur fail on cycle 1 → Ralph rerun on cycle 2 with the reason
    embedded in the implement prompt. Cycle 2 passes all gates."""
    mock_claude.side_effect = [
        (0, "impl v1"),
        _STRUKTUR_FAIL,                 # cycle 1: struktur rejects
        (0, "impl v2"),
        _STRUKTUR_PASS, _DOCS_OK, _FINAL_APPROVE,
    ]
    mock_tests.return_value = (True, "green")

    result = critic_loop(TASK, "pytest", "/project", max_ralph_iterations=5, max_critic_iterations=3)

    assert result is True
    # Cycle-2 implement (index 2) must carry the struktur rejection reason.
    reimpl_prompt = mock_claude.call_args_list[2][0][0]
    assert "wrong abstraction" in reimpl_prompt or "structure" in reimpl_prompt


@patch("orchestrator.runner.run_tests")
@patch("orchestrator.claude.run_claude")
def test_docs_write_escape_routes_to_ralph_with_design_feedback(mock_claude, mock_tests):  # item-028
    """Docs actor invoking the design_issue escape aborts docs+final and
    kicks Ralph back on the next design cycle with the escape reason."""
    mock_claude.side_effect = [
        (0, "impl v1"),
        _STRUKTUR_PASS,
        _DOCS_ESCAPE,                   # cycle 1: docs actor escapes
        (0, "impl v2"),
        _STRUKTUR_PASS, _DOCS_OK, _FINAL_APPROVE,
    ]
    mock_tests.return_value = (True, "green")

    result = critic_loop(TASK, "pytest", "/project", max_ralph_iterations=5, max_critic_iterations=3)

    assert result is True
    reimpl_prompt = mock_claude.call_args_list[3][0][0]
    assert "design_issue_from_docs_attempt" in reimpl_prompt \
        or "leaky abstraction" in reimpl_prompt


@patch("orchestrator.runner.run_tests")
@patch("orchestrator.claude.run_claude")
def test_final_approval_docs_route_reruns_docs_write_within_same_cycle(mock_claude, mock_tests):  # item-028
    """route_to='docs' repeats Phase 3 in the SAME design cycle — no
    Ralph rerun, no new implementation call."""
    mock_claude.side_effect = [
        (0, "impl"),
        _STRUKTUR_PASS,
        _DOCS_OK,       _FINAL_DOCS,    # docs cycle 1: rejected → retry docs
        _DOCS_OK,       _FINAL_APPROVE, # docs cycle 2: approved
    ]
    mock_tests.return_value = (True, "green")

    result = critic_loop(TASK, "pytest", "/project", max_ralph_iterations=5, max_critic_iterations=3)

    assert result is True
    # Only ONE implement call means Ralph did not rerun — routing stayed
    # inside the docs sub-loop.
    assert mock_tests.call_count == 1
    # 2 impl-worthy calls would double the test invocations; single-run
    # confirmation is the meaningful signal here.


@patch("orchestrator.runner.run_tests")
@patch("orchestrator.claude.run_claude")
def test_docs_route_passes_reject_feedback_into_next_docs_write(mock_claude, mock_tests):  # item-028
    """The docs_write retry must include the previous final_approval
    reason as feedback (so the actor knows what to fix)."""
    mock_claude.side_effect = [
        (0, "impl"),
        _STRUKTUR_PASS,
        _DOCS_OK, _FINAL_DOCS,          # docs cycle 1: rejected
        _DOCS_OK, _FINAL_APPROVE,       # docs cycle 2: approved
    ]
    mock_tests.return_value = (True, "green")

    critic_loop(TASK, "pytest", "/project", max_ralph_iterations=5, max_critic_iterations=3)

    # The second docs_write prompt (call index 4) must carry final_approval feedback.
    retry_docs_prompt = mock_claude.call_args_list[4][0][0]
    assert "wrong version" in retry_docs_prompt or "factual_error" in retry_docs_prompt


@patch("orchestrator.runner.run_tests")
@patch("orchestrator.claude.run_claude")
def test_max_docs_cycles_escalates_to_design_route(mock_claude, mock_tests):  # item-028 (Guardrail 3)
    """After MAX_DOCS_CYCLES docs-only rejects, the loop force-routes to
    a design fix — evidence that docs alone are not the problem."""
    from orchestrator import MAX_DOCS_CYCLES
    docs_pairs = []
    for _ in range(MAX_DOCS_CYCLES):
        docs_pairs.append(_DOCS_OK)
        docs_pairs.append(_FINAL_DOCS)          # keeps rejecting to docs
    mock_claude.side_effect = [
        (0, "impl cycle 1"),
        _STRUKTUR_PASS,
        *docs_pairs,                            # exhaust docs cycles
        (0, "impl cycle 2"),                    # escalated → Ralph rerun
        _STRUKTUR_PASS, _DOCS_OK, _FINAL_APPROVE,
    ]
    mock_tests.return_value = (True, "green")

    result = critic_loop(TASK, "pytest", "/project", max_ralph_iterations=5, max_critic_iterations=3)

    assert result is True
    # Ralph ran twice → 2 test-command invocations
    assert mock_tests.call_count == 2
    # Cycle-2 implement prompt must carry the escalation feedback
    reimpl_idx = 2 + 2 * MAX_DOCS_CYCLES        # after impl + struktur + docs_pairs
    reimpl_prompt = mock_claude.call_args_list[reimpl_idx][0][0]
    assert "escalation" in reimpl_prompt.lower() or "factual_error" in reimpl_prompt


@patch("orchestrator.runner.run_tests")
@patch("orchestrator.claude.run_claude")
def test_happy_path_bug_flow_uses_bug_variant_prompts(mock_claude, mock_tests):  # item-028
    """Bug items must run through the same 4-gate sequence via bug_variant
    prompt builders (identical outer flow, different framing)."""
    bug = {"id": "B01-broken", "content": "Reproducer for defect X", "type": "bug", "path": "b.md"}
    mock_claude.side_effect = [
        (0, "fixed"), _STRUKTUR_PASS, _DOCS_OK, _FINAL_APPROVE,
    ]
    mock_tests.return_value = (True, "green")

    result = critic_loop(bug, "pytest", "/project", max_ralph_iterations=5, max_critic_iterations=3)

    assert result is True
    # The struktur prompt (call index 1) must use bug-variant framing.
    struktur_prompt = mock_claude.call_args_list[1][0][0]
    assert "bug" in struktur_prompt.lower() or "fix" in struktur_prompt.lower()


# ═══════════════════════════════════════════════════════════════
#  Integration-level prompt-structure verification (item 030 #7 / #8)
#
#  These tests go one level deeper than the pure routing tests above:
#  they pin the STRUCTURE and CONTENT of the prompts sent on rerun
#  paths, not just that a call happened. Written after two live E2E
#  runs failed to trigger the docs-rerun path (actor was thorough
#  enough to fix everything in cycle 1); the loop-level guarantees
#  need to be locked in synthetically as long as the real path stays
#  rare in practice.
# ═══════════════════════════════════════════════════════════════

@patch("orchestrator.runner.run_tests")
@patch("orchestrator.claude.run_claude")
def test_docs_rerun_prompt_carries_full_review_context(mock_claude, mock_tests):  # item-030 #7
    """When Phase 4 rejects with route_to=docs, the retry docs_write prompt
    must carry not just the reviewer's reason but the FULL actor context
    (task content, mandatory files list, escape-hatch instructions) so the
    actor has everything needed to fix without re-fetching."""
    from orchestrator import MANDATORY_DOC_FILES
    mock_claude.side_effect = [
        (0, "impl"), _STRUKTUR_PASS,
        _DOCS_OK, _FINAL_DOCS,          # docs cycle 1: rejected (route_to=docs)
        _DOCS_OK, _FINAL_APPROVE,       # docs cycle 2: approved
    ]
    mock_tests.return_value = (True, "green")

    result = critic_loop(TASK, "pytest", "/project", max_ralph_iterations=5, max_critic_iterations=3)

    assert result is True
    retry_docs_prompt = mock_claude.call_args_list[4][0][0]

    # Reviewer feedback signals present.
    assert "factual_error" in retry_docs_prompt          # criterion echoed
    assert "wrong version" in retry_docs_prompt          # reason echoed

    # Actor context still fully present (retry is a rehydrated actor call,
    # not a bare feedback ping).
    assert TASK["content"] in retry_docs_prompt          # task body
    for f in MANDATORY_DOC_FILES:                        # mandatory files list
        assert f in retry_docs_prompt
    assert "design_issue" in retry_docs_prompt           # escape hatch still available
    assert "git diff HEAD" in retry_docs_prompt          # inspection instruction

    # Feedback precedes the standard actor prompt so the actor reads WHY
    # they are re-running before the how-to.
    assert retry_docs_prompt.find("wrong version") < retry_docs_prompt.find(TASK["content"])


@patch("orchestrator.runner.run_tests")
@patch("orchestrator.claude.run_claude")
def test_max_docs_cycles_escalation_gives_ralph_labeled_feedback(mock_claude, mock_tests):  # item-030 #8
    """Guardrail 3 escalation must reach Ralph with a LABELED reason
    ('docs cycle escalation (...)'), not a raw criterion — so the next
    implementation attempt understands the docs path was exhausted."""
    from orchestrator import MAX_DOCS_CYCLES
    docs_pairs = []
    for _ in range(MAX_DOCS_CYCLES):
        docs_pairs.append(_DOCS_OK)
        docs_pairs.append(_FINAL_DOCS)          # keeps rejecting to docs
    mock_claude.side_effect = [
        (0, "impl v1"), _STRUKTUR_PASS,
        *docs_pairs,                            # exhaust
        (0, "impl v2"),                         # Ralph re-runs after escalation
        _STRUKTUR_PASS, _DOCS_OK, _FINAL_APPROVE,
    ]
    mock_tests.return_value = (True, "green")

    result = critic_loop(TASK, "pytest", "/project", max_ralph_iterations=5, max_critic_iterations=3)

    assert result is True
    reimpl_idx = 2 + 2 * MAX_DOCS_CYCLES
    reimpl_prompt = mock_claude.call_args_list[reimpl_idx][0][0]

    # The escalation marker must be explicit — otherwise Ralph can't
    # distinguish "final_approval said design" from "docs kept failing
    # so we escalated". The latter is a stronger signal.
    assert "docs cycle escalation" in reimpl_prompt.lower()
    # The final_approval reason from the last docs cycle should carry
    # through so Ralph has actionable context, not just a category.
    assert "wrong version" in reimpl_prompt


@patch("orchestrator.runner.run_tests")
@patch("orchestrator.claude.run_claude")
def test_docs_escape_gives_ralph_labeled_feedback(mock_claude, mock_tests):  # item-030 #7 (escape path)
    """Guardrail 4: docs_write actor escape sends Ralph a LABELED reason
    ('design_issue_from_docs_attempt: ...') so Ralph knows the docs actor
    tapped out mid-write, not that Phase 4 rejected."""
    mock_claude.side_effect = [
        (0, "impl v1"), _STRUKTUR_PASS,
        _DOCS_ESCAPE,                           # cycle 1 escape → back to Ralph
        (0, "impl v2"),
        _STRUKTUR_PASS, _DOCS_OK, _FINAL_APPROVE,
    ]
    mock_tests.return_value = (True, "green")

    result = critic_loop(TASK, "pytest", "/project", max_ralph_iterations=5, max_critic_iterations=3)

    assert result is True
    # Call sequence: 0 impl, 1 struktur, 2 docs_escape, 3 impl-v2, ...
    reimpl_prompt = mock_claude.call_args_list[3][0][0]
    assert "design_issue_from_docs_attempt" in reimpl_prompt
    assert "leaky abstraction" in reimpl_prompt          # escape reason preserved


@patch("orchestrator.runner.run_tests")
@patch("orchestrator.claude.run_claude")
def test_interleaved_struktur_and_docs_failures_route_correctly(mock_claude, mock_tests):  # item-030 #7
    """Mixed-failure state transition:
    design cycle 0: Ralph → struktur FAIL → back to Ralph
    design cycle 1: Ralph → struktur PASS → docs cycle 1 rejects → docs cycle 2 approves
    Exercises the full grid of state transitions in a single task run."""
    mock_claude.side_effect = [
        # Design cycle 0: struktur rejects
        (0, "impl v1"),
        _STRUKTUR_FAIL,
        # Design cycle 1: everything passes but final_approval bounces docs
        (0, "impl v2"),
        _STRUKTUR_PASS,
        _DOCS_OK, _FINAL_DOCS,          # docs cycle 1 route_to=docs
        _DOCS_OK, _FINAL_APPROVE,       # docs cycle 2 approves
    ]
    mock_tests.return_value = (True, "green")

    result = critic_loop(TASK, "pytest", "/project", max_ralph_iterations=5, max_critic_iterations=3)

    assert result is True
    # Ralph ran exactly twice (struktur reject + fresh cycle), NOT thrice.
    assert mock_tests.call_count == 2
    # Cycle-1 (recovered) Ralph implement prompt carries the struktur feedback.
    reimpl_prompt = mock_claude.call_args_list[2][0][0]
    assert "structure:" in reimpl_prompt.lower() or "wrong abstraction" in reimpl_prompt
    # Docs-cycle-2 prompt still has final_approval feedback (not stale struktur).
    docs_retry_prompt = mock_claude.call_args_list[6][0][0]
    assert "wrong version" in docs_retry_prompt or "factual_error" in docs_retry_prompt
    assert "wrong abstraction" not in docs_retry_prompt  # struktur feedback is gone
