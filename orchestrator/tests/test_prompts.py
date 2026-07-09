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
