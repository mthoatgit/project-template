"""Prompt builders for Claude (implement, fix, critic, write-tests), Critic
output parsing, and small formatting helpers.

Option-H DoD-gate prompts (backlog item 028) live at the bottom of the
file: build_struktur_check_prompt / build_docs_write_prompt /
build_final_approval_prompt with their parsers. They use JSON-in-Text
verdicts (schema instructed in the prompt, extracted with a robust
brace-balancing helper). Migration to API-level Tool-Use is tracked in
backlog item 029.
"""
import json
import re

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


# ═══════════════════════════════════════════════════════════════
#  Option-H DoD gates (backlog item 028)
#
#  Sequence: ralph_loop → struktur_check → docs_write → final_approval
#  Consumed by loops.py in step 2 of the 028 rollout.
# ═══════════════════════════════════════════════════════════════

# The seven failure criteria the final_approval reviewer must choose from.
# The split into _DOCS_CRITERIA / _DESIGN_CRITERIA lets the parser derive
# route_to when the reviewer forgets to include it explicitly.
FINAL_APPROVAL_CRITERIA = frozenset({
    "factual_error", "missing_coverage", "inconsistent_docs",
    "leaky_abstraction", "behavior_inconsistency",
    "design_contradicts_other_docs", "scope_beyond_mandatory",
})

_DOCS_CRITERIA = frozenset({
    "factual_error", "missing_coverage", "inconsistent_docs",
})

_DESIGN_CRITERIA = frozenset({
    "leaky_abstraction", "behavior_inconsistency",
    "design_contradicts_other_docs", "scope_beyond_mandatory",
})


def _extract_json_block(text: str) -> dict | None:
    """Extract the last valid JSON object from a mixed prose+JSON response.

    Handles Markdown code fences (```json ... ``` or ``` ... ```) and picks
    the LAST {...} block, since prompts instruct the model to place JSON at
    the end of the response. Returns None if no valid dict is found.

    Robustness matters here because JSON-in-Text is our contract with the
    model — a malformed reply must not silently look approved. Callers use
    the None-return to trigger a safe default (design-first bias).
    """
    # Strip markdown fence markers (keep the content between them).
    cleaned = re.sub(r"```(?:json)?\s*", "", text)
    cleaned = re.sub(r"\s*```", "", cleaned)

    candidates: list[str] = []
    for start in range(len(cleaned)):
        if cleaned[start] != "{":
            continue
        depth = 0
        for end in range(start, len(cleaned)):
            if cleaned[end] == "{":
                depth += 1
            elif cleaned[end] == "}":
                depth -= 1
                if depth == 0:
                    candidates.append(cleaned[start:end + 1])
                    break

    # Last block first — prompts ask for JSON at the response end.
    for candidate in reversed(candidates):
        try:
            result = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(result, dict):
            return result
    return None


# ── Phase 2: Struktur-Check (binary gate) ─────────────────────

def build_struktur_check_prompt(task: dict) -> str:
    """Reviewer prompt for Option-H Phase 2.

    Binary gate that runs after Ralph gets tests green and BEFORE
    docs_write. Purpose: reject structurally-wrong solutions early so we
    don't waste a docs_write cycle on an implementation that would fail
    final_approval anyway. Reviewer inspects the code diff, not the docs.
    """
    return f"""You are a senior software engineer conducting a fast STRUCTURAL
review of a task implementation. Tests already pass — your job is to
decide whether the SOLUTION STRUCTURE is sound before we invest in
updating documentation.

First, inspect the change:
- Run `git diff HEAD` to see what code and tests changed.
- Read the affected implementation files if the diff is not self-
  explanatory.

## Task that was implemented:
{task['content']}

## Evaluate:
- Is this the natural, idiomatic solution an experienced developer would
  choose?
- Is the change scoped correctly (no scope creep, no unrelated edits)?
- Is the abstraction level appropriate (not over- or under-engineered)?
- Are there structural issues that would embarrass the team at merge?

## Do NOT evaluate:
- Documentation drift — that gets fixed in the next phase, do NOT judge
  it here.
- Code formatting, indentation, naming style.

## Response format

You may reason briefly in prose. END your response with a JSON block
matching this schema exactly:

```json
{{"pass": true, "reason": "one-line summary"}}
```
OR
```json
{{"pass": false, "reason": "one-line summary of the structural problem"}}
```
"""


def parse_struktur_check_output(output: str) -> tuple[bool, str]:
    """Parse the Struktur-Check verdict.

    Returns ``(passed, reason)``. Any parse failure or missing ``pass``
    key returns ``(False, "<default reason>")`` — the safe direction is
    to route back to Ralph rather than silently proceed to docs_write.
    """
    data = _extract_json_block(output)
    if data is None or "pass" not in data:
        return False, "verdict could not be parsed — routing back for design fix"
    return bool(data["pass"]), str(data.get("reason", ""))


# ── Phase 3: Docs-Write (actor with escape hatch) ─────────────

def build_docs_write_prompt(task: dict, mandatory_files: list[str]) -> str:
    """Actor prompt for Option-H Phase 3.

    Actor reads the code diff (via `git diff HEAD`, consistent with the
    read-your-own pattern in build_critic_prompt) and updates the
    mandatory documentation files so they describe the new behavior.

    May escape via a JSON block ``{"status": "design_issue", ...}`` when
    the behavior can't be cleanly described (Guardrail 4 in item 028).
    The escape routes the task back to Phase 1 (Ralph).
    """
    file_list = ", ".join(f"`{f}`" for f in mandatory_files)
    return f"""{_GUARDRAILS_NOTICE}

## Docs-Write Phase

Ralph has landed a code+test change for task '{task['id']}' that passed
structural review. Your job: bring the mandatory documentation files
into sync with the new behavior BEFORE the final approval reviewer runs.

Steps:
1. Run `git diff HEAD` and `git status` to see what changed.
2. For each mandatory file, grep for signatures of the OLD behavior —
   old command strings, constant values, workflow steps that no longer
   apply. Update anything stale.
3. Do NOT add new sections for unrelated content. Only update what
   describes the changed behavior.

Mandatory files: {file_list}

## Escape Hatch

If while attempting to describe the new behavior you discover it CANNOT
be cleanly described (leaky abstraction that would require implementation
details in docs, contradicts documented behavior elsewhere, etc.), STOP
writing docs and output ONLY this JSON block as your final response:

```json
{{"status": "design_issue", "reason": "<one-sentence why>"}}
```

This routes the task back to Ralph (Phase 1) for a design fix rather
than papering over an issue in the docs.

## Task specification (for context)

{task['content']}

Otherwise: update docs silently. No explicit success signal is required.
"""


def parse_docs_write_output(output: str) -> tuple[str, str]:
    """Parse the docs_write actor's result.

    Returns ``("ok", "")`` on the normal path (no escape signal in the
    output), or ``("design_issue", reason)`` when the actor invoked the
    escape hatch. Docs_write is an ACTION phase, not a verdict phase —
    absence of JSON is the normal-path signal, not a parser failure.
    """
    data = _extract_json_block(output)
    if data is None:
        return "ok", ""
    if data.get("status") == "design_issue":
        return "design_issue", str(data.get("reason", ""))
    return "ok", ""


# ── Phase 4: Final-Approval (3-way verdict) ───────────────────

def build_final_approval_prompt(task: dict, mandatory_files: list[str]) -> str:
    """Reviewer prompt for Option-H Phase 4.

    3-way verdict combining code + docs review: approve → commit; reject
    route_to="docs" → Phase 3 repeats; reject route_to="design" → Phase 1
    repeats. Criterion enum forces explicit classification. Design-first
    bias is instructed in prose: false-positive design costs one Ralph
    run, missed design bug ships broken code.
    """
    file_list = ", ".join(f"`{f}`" for f in mandatory_files)
    return f"""You are a senior software engineer conducting the FINAL approval
review of a task implementation. Both code+tests AND mandatory docs have
already been updated in the working tree.

First, inspect the change:
- Run `git diff HEAD` to see all pending changes (code + tests + docs).
- Run `git status` to see file-level scope.

## Task that was implemented:
{task['content']}

## Mandatory documentation files (must be consistent with the code):
{file_list}

## Seven failure criteria

Classify any problem you find into exactly ONE of these seven criteria.
Each criterion maps to a fixed routing decision:

route_to = "docs" (docs update needed, code is fine):
- factual_error      : Docs contain factual mistakes (wrong command,
                       wrong version, typo in a load-bearing string).
- missing_coverage   : A feature exists in the code but is not described
                       anywhere in the mandatory docs.
- inconsistent_docs  : Docs contradict each other (README says X,
                       CLAUDE.md says Y).

route_to = "design" (implementation-level fix needed, docs are a symptom):
- leaky_abstraction              : Behavior cannot be described without
                                   implementation details.
- behavior_inconsistency         : Docs would need to describe
                                   contradictory behavior.
- design_contradicts_other_docs  : Code violates contracts documented
                                   elsewhere.
- scope_beyond_mandatory         : Change requires touching files
                                   outside the mandatory list.

## Design-first bias

WHEN IN DOUBT, choose route_to = "design". A false-positive design flag
costs one extra Ralph iteration; a missed design bug ships broken code.

## Response format

You may reason in prose above the JSON. END your response with a JSON
block matching this schema exactly:

```json
{{"approve": true, "route_to": null, "criterion": null, "reason": "..."}}
```
OR
```json
{{"approve": false, "route_to": "docs", "criterion": "factual_error", "reason": "..."}}
```
OR
```json
{{"approve": false, "route_to": "design", "criterion": "leaky_abstraction", "reason": "..."}}
```
"""


def parse_final_approval_output(output: str) -> tuple[str, str, str]:
    """Parse the 3-way final-approval verdict.

    Returns ``(verdict, criterion, reason)`` where ``verdict`` is one of
    ``"approve"``, ``"docs"``, or ``"design"``.

    Robustness rules (design-first bias per item 028):
    - Unparseable output → ``("design", "", "<default reason>")``.
    - Unknown ``criterion`` → returned as ``""`` (reason carries the info).
    - Missing ``route_to`` but a valid criterion is present → derive
      route from the criterion's category.
    - Missing both → fall back to ``"design"``.
    """
    data = _extract_json_block(output)
    if data is None:
        return "design", "", "verdict could not be parsed — routing to design as safe default"

    if data.get("approve") is True:
        return "approve", "", str(data.get("reason", ""))

    criterion_raw = data.get("criterion")
    criterion = criterion_raw if criterion_raw in FINAL_APPROVAL_CRITERIA else ""

    route_raw = data.get("route_to")
    if route_raw in ("docs", "design"):
        route = route_raw
    elif criterion in _DOCS_CRITERIA:
        route = "docs"
    elif criterion in _DESIGN_CRITERIA:
        route = "design"
    else:
        route = "design"

    return route, criterion, str(data.get("reason", ""))
