"""Tests for orchestrator.prompts — prompt builders, Critic parsing (REQ-16,
REQ-17, REQ-18, REQ-24, REQ-30) and the protected-file notice (REQ-39)."""
from __future__ import annotations

import pytest

from orchestrator import (
    build_critic_prompt,
    build_fix_prompt,
    build_implement_prompt,
    build_write_tests_prompt,
    parse_critic_output,
    # Option-H DoD gates (backlog item 028)
    build_struktur_check_prompt, parse_struktur_check_output,
    build_docs_write_prompt, parse_docs_write_output,
    build_final_approval_prompt, parse_final_approval_output,
    FINAL_APPROVAL_CRITERIA,
)

from orchestrator.tests.helpers import TASK, task_content_present


# ─────────────────────────────────────────────────────────────
#  REQ-17  parse_critic_output: APPROVED / REJECTED
# ─────────────────────────────────────────────────────────────

def test_parse_critic_output_approved():  # REQ-17
    approved, weaknesses = parse_critic_output("APPROVED — approach is clean and idiomatic")
    assert approved is True
    assert weaknesses == ""


def test_parse_critic_output_rejected():  # REQ-17
    output = "REJECTED\n- God class with too many responsibilities\n- Missing abstraction layer"
    approved, weaknesses = parse_critic_output(output)
    assert approved is False
    assert "God class" in weaknesses


def test_parse_critic_output_empty_treated_as_rejected():  # REQ-17
    approved, _ = parse_critic_output("")
    assert approved is False


# ─────────────────────────────────────────────────────────────
#  REQ-16  Critic prompt covers design, not style
# ─────────────────────────────────────────────────────────────

def test_build_critic_prompt_covers_design_not_style():  # REQ-16
    prompt = build_critic_prompt(TASK)
    assert "design" in prompt.lower() or "pattern" in prompt.lower()
    assert "Do NOT evaluate" in prompt
    assert "formatting" in prompt.lower() or "indentation" in prompt.lower()


# ─────────────────────────────────────────────────────────────
#  REQ-18  re-implementation receives feedback but not rejected code
# ─────────────────────────────────────────────────────────────

def test_implement_prompt_without_critic_feedback():  # REQ-18
    prompt = build_implement_prompt(TASK, critic_feedback=None)
    assert "rejected" not in prompt.lower()
    assert task_content_present(prompt)


def test_implement_prompt_with_critic_feedback_no_old_code():  # REQ-18
    feedback = "- God class with too many responsibilities"
    prompt = build_implement_prompt(TASK, critic_feedback=feedback)
    assert "God class" in prompt          # feedback is included
    assert "rejected code" not in prompt  # rejected code is not included
    assert "scratch" in prompt.lower()    # explicit fresh-start instruction
    assert task_content_present(prompt)


# ─────────────────────────────────────────────────────────────
#  REQ-24  revert_context injected into first task's implement prompt
# ─────────────────────────────────────────────────────────────

def test_implement_prompt_contains_revert_context():  # REQ-24
    context = "Previous run failed with: 5 assertion errors"
    prompt = build_implement_prompt(TASK, revert_context=context)
    assert "5 assertion errors" in prompt
    assert "Rolled Back" in prompt
    assert TASK["content"] in prompt


def test_implement_prompt_with_both_revert_and_critic_feedback():  # REQ-24 + REQ-18
    context = "Previous run failed with: 3 test failures"
    feedback = "- Missing abstraction layer"
    prompt = build_implement_prompt(TASK, critic_feedback=feedback, revert_context=context)
    assert "3 test failures" in prompt
    assert "Missing abstraction layer" in prompt
    assert TASK["content"] in prompt


# ─────────────────────────────────────────────────────────────
#  REQ-30  build_write_tests_prompt — content + language-neutral
# ─────────────────────────────────────────────────────────────

def test_build_write_tests_prompt_contains_task_and_doc():  # REQ-30
    prompt = build_write_tests_prompt(TASK, "# Scenarios\n- scenario A")

    assert TASK["id"] in prompt
    assert TASK["content"] in prompt
    assert "# Scenarios" in prompt
    # Neutral, cross-language prohibitions — no "pytest.skip" / "assert False" baked in.
    assert "always-true" in prompt.lower()
    assert "test-skipping" in prompt.lower()
    assert "production" in prompt.lower() or "source" in prompt.lower()


def test_build_write_tests_prompt_is_language_neutral():  # REQ-30
    """The prompt must not force pytest / Python vocabulary onto tasks in
    other ecosystems (Flutter, Java, Rust, ...). Language-specific tokens
    only appear as examples of *what the unimplemented marker looks like*,
    never as commands."""
    prompt = build_write_tests_prompt(TASK, "# doc")

    # Forbidden as prescriptions:
    assert "pytest.skip" not in prompt        # Python-only skip mechanism
    # Language markers may appear only in the "for example" list, alongside
    # at least one other ecosystem. Verify the list is present.
    assert "NotImplementedError" in prompt    # Python example
    assert "UnimplementedError" in prompt     # Dart example
    assert "UnsupportedOperationException" in prompt  # Java example


# ─────────────────────────────────────────────────────────────
#  REQ-39  Protected-file notice appears in code-writing prompts,
#          absent from Critic prompt
# ─────────────────────────────────────────────────────────────

@pytest.mark.parametrize("builder,extra_args", [
    ("build_implement_prompt",   ()),
    ("build_write_tests_prompt", ("test design content",)),
])
def test_code_writing_prompts_include_protection_notice(builder, extra_args):  # REQ-39
    import orchestrator
    fn = getattr(orchestrator, builder)
    prompt = fn(TASK, *extra_args)
    # Notice must list BOTH the package path AND the test file explicitly.
    assert "orchestrator/" in prompt
    assert "test_orchestrator.py" in prompt
    assert "OFF-LIMITS" in prompt or "off-limits" in prompt.lower()


def test_build_fix_prompt_includes_protection_notice():  # REQ-39
    prompt = build_fix_prompt(TASK, "some test output", 1)
    assert "orchestrator/" in prompt
    assert "test_orchestrator.py" in prompt


def test_build_critic_prompt_does_not_include_protection_notice():  # REQ-39
    # The Critic returns text only, doesn't write code — the notice would be
    # noise. Assert it's absent to pin the design choice.
    prompt = build_critic_prompt(TASK)
    assert "OFF-LIMITS" not in prompt


# ─────────────────────────────────────────────────────────────
#  REQ-41  Code-writing prompts forbid `git commit`; Critic exempt.
# ─────────────────────────────────────────────────────────────

@pytest.mark.parametrize("builder,extra_args", [
    ("build_implement_prompt",   ()),
    ("build_fix_prompt",         ("test failure output", 1)),
    ("build_write_tests_prompt", ("test design content",)),
])
def test_code_writing_prompts_forbid_git_commit(builder, extra_args):  # REQ-41
    """Claude must not create commits during implementation — the orchestrator
    owns the single 'one commit per task' step (REQ-21)."""
    import orchestrator
    fn = getattr(orchestrator, builder)
    prompt = fn(TASK, *extra_args)
    assert "git commit" in prompt
    assert "DO NOT" in prompt or "MUST NOT" in prompt
    # Positive callout: reading git history is still allowed so we don't
    # accidentally lock Claude out of useful diagnostic commands.
    assert "git log" in prompt or "git status" in prompt or "git diff" in prompt


def test_build_critic_prompt_does_not_forbid_git_commit():  # REQ-41
    # Critic only reads and outputs a verdict — no notice needed.
    prompt = build_critic_prompt(TASK)
    assert "git commit" not in prompt.lower()


# ═══════════════════════════════════════════════════════════════
#  Option-H DoD gates (backlog item 028)
# ═══════════════════════════════════════════════════════════════

# ─── Struktur-Check (Phase 2) ─────────────────────────────────

def test_build_struktur_check_prompt_contains_task_and_json_schema():  # item-028
    prompt = build_struktur_check_prompt(TASK)
    assert TASK["content"] in prompt
    assert "git diff HEAD" in prompt          # inspection instruction
    assert '"pass"' in prompt                 # JSON schema shown
    # Not the actor — no protection notice, no git-commit forbid.
    assert "OFF-LIMITS" not in prompt
    assert "DO NOT run `git commit`" not in prompt


def test_build_struktur_check_prompt_defers_docs_review():  # item-028
    """Phase 2 must NOT evaluate docs — that's Phase 4's job."""
    prompt = build_struktur_check_prompt(TASK)
    assert "next phase" in prompt.lower() or "phase" in prompt.lower()
    assert "documentation" in prompt.lower() or "docs" in prompt.lower()


def test_parse_struktur_check_output_pass():  # item-028
    out = 'Structure looks clean.\n\n```json\n{"pass": true, "reason": "clean split"}\n```'
    passed, reason = parse_struktur_check_output(out)
    assert passed is True
    assert reason == "clean split"


def test_parse_struktur_check_output_fail():  # item-028
    out = '{"pass": false, "reason": "wrong abstraction level"}'
    passed, reason = parse_struktur_check_output(out)
    assert passed is False
    assert "abstraction" in reason


def test_parse_struktur_check_output_no_json_defaults_to_fail():  # item-028
    """Design-first bias: unparseable → not passing."""
    passed, reason = parse_struktur_check_output("Looks good to me.")
    assert passed is False
    assert reason  # non-empty default reason


def test_parse_struktur_check_output_missing_pass_key_defaults_to_fail():  # item-028
    passed, _ = parse_struktur_check_output('{"reason": "forgot the pass key"}')
    assert passed is False


# ─── Docs-Write (Phase 3) ─────────────────────────────────────

def test_build_docs_write_prompt_contains_task_and_mandatory_files():  # item-028
    prompt = build_docs_write_prompt(TASK, ["README.md", "CLAUDE.md"])
    assert TASK["content"] in prompt
    assert "README.md" in prompt
    assert "CLAUDE.md" in prompt
    assert "git diff HEAD" in prompt
    assert "design_issue" in prompt           # escape hatch documented


def test_build_docs_write_prompt_includes_guardrails():  # item-028 + REQ-39/41
    """Actor writes files, so both protected-files and no-commit notices apply."""
    prompt = build_docs_write_prompt(TASK, ["README.md"])
    assert "orchestrator/" in prompt          # protected-files notice
    assert "test_orchestrator.py" in prompt
    assert "git commit" in prompt             # no-commit forbid
    assert "DO NOT" in prompt or "MUST NOT" in prompt


def test_parse_docs_write_output_no_json_is_ok():  # item-028
    """docs_write is an action phase; no JSON = normal path (silently done)."""
    status, reason = parse_docs_write_output("Updated README and CLAUDE.md.")
    assert status == "ok"
    assert reason == ""


def test_parse_docs_write_output_escape_signal():  # item-028
    out = '{"status": "design_issue", "reason": "leaky abstraction discovered"}'
    status, reason = parse_docs_write_output(out)
    assert status == "design_issue"
    assert "leaky" in reason


def test_parse_docs_write_output_status_ok_json_treated_as_ok():  # item-028
    status, _ = parse_docs_write_output('{"status": "ok"}')
    assert status == "ok"


# ─── Final-Approval (Phase 4) ─────────────────────────────────

def test_build_final_approval_prompt_lists_all_seven_criteria():  # item-028
    prompt = build_final_approval_prompt(TASK, ["README.md", "CLAUDE.md"])
    for criterion in FINAL_APPROVAL_CRITERIA:
        assert criterion in prompt


def test_build_final_approval_prompt_covers_code_and_docs():  # item-028
    prompt = build_final_approval_prompt(TASK, ["README.md"])
    assert TASK["content"] in prompt
    assert "README.md" in prompt
    assert "docs" in prompt.lower()
    assert "git diff HEAD" in prompt          # inspects the diff
    # Not the actor — no protection notice, no commit forbid.
    assert "OFF-LIMITS" not in prompt
    assert "DO NOT run `git commit`" not in prompt


def test_build_final_approval_prompt_states_design_first_bias():  # item-028
    """The prompt must make the safety default explicit."""
    prompt = build_final_approval_prompt(TASK, ["README.md"])
    assert "design" in prompt.lower()
    assert "doubt" in prompt.lower() or "bias" in prompt.lower()


def test_parse_final_approval_output_approve():  # item-028
    out = 'Everything checks out.\n{"approve": true, "route_to": null, "criterion": null, "reason": "clean"}'
    verdict, criterion, reason = parse_final_approval_output(out)
    assert verdict == "approve"
    assert criterion == ""
    assert reason == "clean"


def test_parse_final_approval_output_route_to_docs():  # item-028
    out = '{"approve": false, "route_to": "docs", "criterion": "factual_error", "reason": "wrong version in README"}'
    verdict, criterion, reason = parse_final_approval_output(out)
    assert verdict == "docs"
    assert criterion == "factual_error"
    assert "wrong version" in reason


def test_parse_final_approval_output_route_to_design():  # item-028
    out = '{"approve": false, "route_to": "design", "criterion": "leaky_abstraction", "reason": "docs would need impl details"}'
    verdict, criterion, _ = parse_final_approval_output(out)
    assert verdict == "design"
    assert criterion == "leaky_abstraction"


def test_parse_final_approval_output_derives_route_from_docs_criterion():  # item-028
    """If reviewer forgets route_to but names a docs-side criterion, derive it."""
    out = '{"approve": false, "criterion": "inconsistent_docs", "reason": "README says X, CLAUDE.md says Y"}'
    verdict, criterion, _ = parse_final_approval_output(out)
    assert verdict == "docs"
    assert criterion == "inconsistent_docs"


def test_parse_final_approval_output_derives_route_from_design_criterion():  # item-028
    out = '{"approve": false, "criterion": "behavior_inconsistency", "reason": "..."}'
    verdict, _, _ = parse_final_approval_output(out)
    assert verdict == "design"


def test_parse_final_approval_output_unparseable_defaults_to_design():  # item-028
    """Design-first bias: any parse failure routes to design."""
    verdict, criterion, reason = parse_final_approval_output("No JSON here, just prose.")
    assert verdict == "design"
    assert criterion == ""
    assert reason  # non-empty default reason


def test_parse_final_approval_output_unknown_criterion_returned_as_empty():  # item-028
    """Reviewer invented a criterion → we don't propagate it, but keep the verdict."""
    out = '{"approve": false, "route_to": "docs", "criterion": "vibes_off", "reason": "..."}'
    verdict, criterion, _ = parse_final_approval_output(out)
    assert verdict == "docs"    # honored: route_to was explicit and valid
    assert criterion == ""      # rejected: unknown enum value


def test_parse_final_approval_output_missing_route_and_criterion_defaults_to_design():  # item-028
    out = '{"approve": false, "reason": "something is off"}'
    verdict, _, _ = parse_final_approval_output(out)
    assert verdict == "design"


# ─── JSON extraction robustness ───────────────────────────────

def test_parse_takes_last_json_block_when_multiple_present():  # item-028
    """Reviewer sometimes shows an example schema mid-response; last block wins."""
    out = (
        'The schema is:\n```json\n{"pass": false, "reason": "example"}\n```\n'
        'My actual verdict:\n```json\n{"pass": true, "reason": "actual verdict"}\n```'
    )
    passed, reason = parse_struktur_check_output(out)
    assert passed is True
    assert reason == "actual verdict"


def test_parse_handles_plain_code_fence_without_language_tag():  # item-028
    out = 'Analysis...\n```\n{"pass": true, "reason": "ok"}\n```'
    passed, _ = parse_struktur_check_output(out)
    assert passed is True


def test_parse_handles_nested_braces_in_json():  # item-028
    """JSON with a nested dict as value must not confuse the brace counter."""
    out = '{"approve": false, "route_to": "docs", "criterion": "factual_error", "reason": "see {ctx}"}'
    verdict, criterion, reason = parse_final_approval_output(out)
    assert verdict == "docs"
    assert criterion == "factual_error"
    assert "{ctx}" in reason


def test_parse_ignores_earlier_malformed_json_uses_last_valid():  # item-028
    out = (
        '```json\n{malformed, no quotes}\n```\n'
        '```json\n{"pass": false, "reason": "second wins"}\n```'
    )
    passed, reason = parse_struktur_check_output(out)
    assert passed is False
    assert reason == "second wins"
