"""Prompt builders for Claude (implement, fix, critic, write-tests), Critic
output parsing, and small formatting helpers."""

# Both notices list their targets explicitly (rather than templating from
# constants) so the phrasing is stable and human-friendly.
_PROTECTED_FILES_NOTICE = (
    "IMPORTANT — the following are the orchestrator's own tooling and are "
    "OFF-LIMITS. You MUST NOT create, modify, or delete anything under "
    "these paths:\n"
    "  - orchestrator/     (the whole package)\n"
    "  - test_orchestrator.py\n"
    "If you believe a change is required, STOP and explain the reason in "
    "plain text as your response — do NOT edit them. Any edit will be "
    "automatically reverted."
)

# The orchestrator owns the single commit per task (REQ-21). Claude may
# stage / rearrange / delete files freely, but MUST NOT create git commits
# — otherwise the orchestrator's post-task commit finds nothing to stage
# and the "one commit per task" invariant breaks (REQ-41).
_NO_COMMIT_NOTICE = (
    "IMPORTANT — DO NOT run `git commit` (or any command that creates a "
    "commit — including `git commit --amend`, `git revert`, `git merge`, "
    "`git cherry-pick`, ...). The orchestrator produces exactly one "
    "commit per task after tests pass and the Critic approves. Your job "
    "is to leave the working tree in the desired state; the orchestrator "
    "handles staging and committing. Reading git history (`git log`, "
    "`git diff`, `git status`) is fine."
)

_GUARDRAILS_NOTICE = _PROTECTED_FILES_NOTICE + "\n\n" + _NO_COMMIT_NOTICE


def build_implement_prompt(
    task: dict,
    critic_feedback: str | None = None,
    revert_context: str | None = None,
) -> str:
    """Build the implementation prompt for Claude.

    ``critic_feedback``: included when the Critic rejected a previous
                         attempt; the rejected code is deliberately omitted
                         to prevent anchoring to the wrong approach (REQ-18).
    ``revert_context``:  included when a previous commit was rolled back
                         due to test failures; tells Claude what broke
                         (REQ-24). Both can be present simultaneously.
    """
    sections: list[str] = []

    if revert_context:
        sections.append(
            f"## Warning — Previous Implementation Was Rolled Back\n"
            f"{revert_context}\n\n"
            f"Implement this task carefully so it does not break any existing tests."
        )

    if critic_feedback:
        sections.append(
            f"A previous implementation passed all tests but was rejected in "
            f"design review for the following reasons:\n\n"
            f"## Design review concerns:\n{critic_feedback}\n\n"
            f"Rethink the approach from scratch. You may delete and recreate "
            f"existing files. Do not patch or reference the previous implementation."
        )

    if not sections:
        sections.append(
            "Implement the following task exactly as specified.\n"
            "Read the relevant existing files first, then write all necessary code.\n"
            "Do not add features beyond what the task requires."
        )

    sections.append(f"## Task ID: {task['id']}\n\n{task['content']}")
    return _GUARDRAILS_NOTICE + "\n\n" + "\n\n".join(sections)


def build_fix_prompt(task: dict, errors: str, iteration: int) -> str:
    return f"""{_GUARDRAILS_NOTICE}

The implementation of task '{task['id']}' failed the tests (attempt {iteration}).
Analyze the test output below, identify the root cause, and fix the code.

## Test Failures:
{errors}

## Original Task Specification:
{task['content']}

Fix the implementation so that all tests pass. Do not change the tests themselves.
"""


def build_critic_prompt(task: dict) -> str:
    """Build the adversarial design-review prompt for the Critic.

    The Critic's mandate is to find problems, not to confirm the
    implementation. It receives no rationale from the implementer to
    avoid anchoring bias.
    """
    return f"""You are a senior software engineer conducting an adversarial design review.
Your role is to find fundamental problems with the solution approach — not to confirm it.
Be skeptical. If the approach is wrong, say so clearly.

First, read the implementation files relevant to this task.

## Task that was implemented:
{task['content']}

## Evaluate:
- Is this the natural, idiomatic solution an experienced developer would choose?
- Are appropriate design patterns used for the context (not over- or under-engineered)?
- Does it follow clean code principles at design level: Single Responsibility,
  correct abstraction level, no structural DRY violations?
- Would a senior developer accept this approach in a PR review — not reluctantly,
  but because the approach is genuinely good?
- Does it avoid anti-patterns and solutions that technically work but no
  experienced developer would choose?

## Do NOT evaluate:
- Code formatting, indentation, or whitespace
- Naming style conventions (camelCase vs snake_case etc.)
- Comment style or documentation formatting

## Response format (follow exactly):
If the approach is solid:
  APPROVED — [one-line reason]

If there are fundamental problems:
  REJECTED
  - [specific design concern 1]
  - [specific design concern 2]
  ...

Do not suggest fixes. Only identify what is wrong with the current approach.
"""


def build_write_tests_prompt(task: dict, test_doc_content: str) -> str:
    return (
        f"{_GUARDRAILS_NOTICE}\n\n"
        f"Read the task specification and test design document, "
        f"then write the tests for this task.\n\n"
        f"Rules:\n"
        f"- Write real, meaningful tests with concrete assertions.\n"
        f"- No stubs, no always-true assertions, no test-skipping mechanisms.\n"
        f"- Tests must FAIL because the implementation is not yet written — "
        f"the skeleton throws the language's \"unimplemented\" marker "
        f"(NotImplementedError in Python, UnimplementedError in Dart, "
        f"UnsupportedOperationException in Java, todo!() in Rust, etc.). "
        f"Failures should be structural, not because your assertions are wrong.\n"
        f"- Create a new test file — do not modify any existing test files.\n"
        f"- Do not write or modify any production / source code in this step.\n\n"
        f"## Task {task['id']}:\n{task['content']}\n\n"
        f"## Test Design Document:\n{test_doc_content}\n\n"
        f"Write only the tests for task {task['id']}. "
        f"After writing, the tests should fail because the implementation "
        f"raises its \"unimplemented\" marker — not because assertions are wrong."
    )


def parse_critic_output(output: str) -> tuple[bool, str]:
    """Parse the Critic's verdict.

    Returns ``(approved, weaknesses)``. ``weaknesses`` is empty string when
    approved. Scans all lines so that CLI preamble messages (e.g. Claude's
    stdin warning) before the actual APPROVED/REJECTED verdict do not
    cause a false rejection.
    """
    for line in output.strip().splitlines():
        if line.strip().upper().startswith("APPROVED"):
            return True, ""
    return False, output.strip()


def format_elapsed(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"
