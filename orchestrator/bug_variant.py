"""Bug-flow variants of the four prompt builders in ``prompts.py``.

Same function signatures as ``prompts.build_*``, different framing:
tasks say "implement this new feature", bugs say "make the pinned
regression test go green with a minimal fix". Loops.py picks the module
based on ``item['type']``.

Also exposes ``is_class_b(item)`` — a one-liner check the dispatcher
uses to skip Class B bugs (human-only per ``workflow-bugs`` skill).
"""
from . import prompts as _p


def is_class_b(item: dict) -> bool:
    """True iff this is a Class B bug (structurally not test-catchable)."""
    return item.get("type") == "bug" and item.get("class_") == "B"


def build_write_tests_prompt(item: dict, test_doc_content: str) -> str:
    """Ask Claude to write ONE regression test that captures the bug.

    Anchored at the entry point per ``workflow-tests``. Must be RED
    against the current unfixed code — the reproducer bail-out in
    ``loops.write_tests_phase`` verifies that.
    """
    return (
        f"{_p._GUARDRAILS_NOTICE}\n\n"
        f"You are handling a reported bug. Your FIRST step is to write a "
        f"REGRESSION TEST that captures the exact defect described in the "
        f"bug report — before touching any implementation code.\n\n"
        f"Rules:\n"
        f"- Read the bug file's Symptom and Reproduction sections carefully.\n"
        f"- Add exactly ONE new test case that reproduces the reported failure.\n"
        f"- Anchor at the entry point: root widget / main() for UI, real HTTP "
        f"call with an external Origin header for a web API, main() for a CLI. "
        f"Not the internal API in isolation.\n"
        f"- Add the test to the appropriate EXISTING test file that already "
        f"targets this area (mirror the file's conventions). Create a new "
        f"file only if no fit exists.\n"
        f"- The test must assert against the EXPECTED behavior (not the "
        f"buggy actual behavior) — so it FAILS on the current code and will "
        f"pass once the bug is fixed.\n"
        f"- Do NOT touch any production/source code in this step.\n"
        f"- Do NOT modify any existing tests.\n\n"
        f"## Bug Report:\n{item['content']}\n\n"
        f"## Existing Test Design Document:\n{test_doc_content}\n\n"
        f"Write only the regression test. After you're done, it MUST FAIL "
        f"against the current (unfixed) code — that failure is the proof "
        f"the reproducer works."
    )


def build_implement_prompt(
    item: dict,
    critic_feedback: str | None = None,
    revert_context: str | None = None,
) -> str:
    """Ask Claude to fix the bug with a minimal, root-cause change.

    The regression test written in the pre-step is PINNED — Claude may
    not modify it. Only production code changes are allowed.
    """
    sections: list[str] = []

    if revert_context:
        sections.append(
            f"## Warning — Previous Fix Was Rolled Back\n"
            f"{revert_context}\n\n"
            f"Fix this bug carefully so no existing tests regress."
        )

    if critic_feedback:
        sections.append(
            f"A previous fix passed the regression test but was rejected "
            f"in design review for the following reasons:\n\n"
            f"## Design review concerns:\n{critic_feedback}\n\n"
            f"Rethink the fix from scratch. You may delete and recreate "
            f"the changes you made. Do not patch the previous fix."
        )

    if not sections:
        sections.append(
            "Fix the bug described below. A regression test has already "
            "been written that captures this defect — your job is to make "
            "that test pass with a MINIMAL, targeted code change.\n\n"
            "Rules:\n"
            "- The regression test just written is PINNED. Do NOT modify "
            "it in any way — assertions, arrange, fixtures all stay.\n"
            "- Change ONLY the production code needed to make the "
            "regression test pass.\n"
            "- Address the ROOT CAUSE, not the visible symptom. If a "
            "workaround is unavoidable, add a code comment explaining why.\n"
            "- Do NOT expand scope. If you notice other issues, leave them.\n"
            "- The full test suite must remain green — nothing else may "
            "regress."
        )

    sections.append(f"## Bug ID: {item['id']}\n\n{item['content']}")
    return _p._GUARDRAILS_NOTICE + "\n\n" + "\n\n".join(sections)


def build_fix_prompt(item: dict, errors: str, iteration: int) -> str:
    """Retry prompt for the Ralph Loop when the fix attempt didn't pass."""
    return f"""{_p._GUARDRAILS_NOTICE}

The fix attempt for bug '{item['id']}' still failed tests (attempt {iteration}).
Analyze the failures below, identify the root cause, and adjust the code.

## Test Failures:
{errors}

## Original Bug Report:
{item['content']}

Rules:
- The regression test is PINNED. Do NOT modify it — only fix production code.
- Address root cause, not symptoms.
- Keep the change minimal — no unrelated edits.
"""


def build_critic_prompt(item: dict) -> str:
    """Adversarial review focused on root-cause vs symptom-patch and scope creep."""
    return f"""You are a senior software engineer conducting a bug-fix review.
Your role is to find problems with the fix approach — not to confirm it.
Be skeptical. If the fix is a symptomatic patch, say so.

First, read the fix diff and the surrounding code.

## Bug that was fixed:
{item['content']}

## Evaluate:
- Does the fix address the ROOT CAUSE, or does it only patch the visible symptom?
- Is the scope MINIMAL — does it touch only code needed to make the regression test pass?
- Are there any changes outside the reported bug's scope (drive-by refactors, unrelated tweaks)?
- Would the fix hold up against similar-shaped bugs, or is it a specific patch that leaves the underlying issue in place elsewhere?

## Do NOT evaluate:
- The regression test itself (treat as pinned)
- Code formatting, indentation, whitespace
- Naming style conventions

## Response format (follow exactly):
If the fix is solid:
  APPROVED — [one-line reason]

If there are problems:
  REJECTED
  - [specific concern 1]
  - [specific concern 2]
  ...

Do not suggest fixes. Identify what is wrong with the current approach.
"""
