"""The nested loops that drive each task through TDD + DoD gates:

- ``ralph_loop``: inner correctness loop (implement → test → fix)
- ``critic_loop``: outer solution-quality loop — Option-H DoD gates
  (correctness → struktur_check → docs_write → final_approval).
  Legacy name kept; historically it wrapped a single Critic-Actor review.
- ``write_tests_phase``: pre-implementation test-writing step
"""
import time

# Module-attribute access (``runner.run_tests``, ``claude.run_claude``, ...)
# so @patch("orchestrator.runner.run_tests") etc. propagate into these
# callers — see docs/orchestrator-requirements.md.
from . import bug_variant, claude, prompts, runner, status, tasks
from .config import (
    MAX_ERROR_CHARS, STUCK_STREAK_THRESHOLD,
    MAX_DOCS_CYCLES, MANDATORY_DOC_FILES,
)


def _prompts_for(item: dict):
    """Return the prompt module for this item — bug_variant for bugs,
    prompts for tasks. Both modules expose the same seven builders with
    the same signatures: build_write_tests_prompt, build_implement_prompt,
    build_fix_prompt, build_critic_prompt (legacy, unused since Option-H),
    build_struktur_check_prompt, build_docs_write_prompt,
    build_final_approval_prompt."""
    return bug_variant if item.get("type") == "bug" else prompts


def write_tests_phase(
    task: dict,
    test_cmd: str,
    test_doc_content: str,
    project_dir: str,
) -> tuple[str, bool]:
    """Call Claude to write tests, then verify they fail (REQ-30, REQ-31, REQ-32).

    Tasks: Claude creates a new test file; presence of the new file is
    a precondition. Bugs: Claude appends a regression scenario to an
    existing test file; no new file is required, and a passing verify
    is a HARD FAIL (reproducer doesn't reproduce — see workflow-bugs).
    """
    is_bug = task.get("type") == "bug"
    kind = "Regression Test" if is_bug else "Write Tests"
    print(f"\n[{kind}] '{task['id']}'")
    prompt = _prompts_for(task).build_write_tests_prompt(task, test_doc_content)
    rc, _ = claude.run_claude(prompt, project_dir)
    if rc != 0:
        print(f"  [!] claude exited with code {rc}")

    if not is_bug:
        test_files = runner.detect_task_test_files(project_dir)
        if not test_files:
            print("  [ERROR] No test files were created — aborting task")
            return test_cmd, False
        print(f"  Created: {', '.join(test_files)}")

    # Framework-agnostic: the project's --test-cmd runs *all* tests. The
    # new scenario is the only thing that should be failing now — a red
    # run here means the reproducer / new tests are failing as expected.
    print(f"\n[Verify]  {test_cmd}")
    passed, verify_output = runner.run_tests(test_cmd, project_dir)
    if passed:
        if is_bug:
            print("  [ERROR] Regression test passes without a fix — reproducer doesn't reproduce.")
            print("          Bug is misdescribed or targets the wrong entry point. Human triage required.")
            return test_cmd, False
        print("  [WARNING] Tests pass before implementation — proceeding anyway")
    else:
        fail_count = runner.extract_failure_count(verify_output)
        count_str = str(fail_count) if fail_count is not None else "?"
        print(f"  [OK] {count_str} test(s) failing as expected")

    return test_cmd, True


def ralph_loop(
    task: dict,
    test_cmd: str,
    project_dir: str,
    max_iterations: int,
    critic_feedback: str | None = None,
    revert_context: str | None = None,
) -> bool:
    """Inner correctness loop: implement → test → fix → repeat.

    Iteration 0 asks Claude to implement the task from scratch, optionally
    including Critic feedback (REQ-18) or revert context (REQ-24).
    Iterations 1..N ask Claude to fix the code using the previous test
    output. The loop exits as soon as tests pass or one of the four exit
    criteria fires.

    Returns True if the task's tests eventually pass, False otherwise.
    """
    errors: str | None = None
    prev_output: str | None = None
    prev_fail_count: int | None = None
    stuck_streak = 0

    for iteration in range(max_iterations + 1):
        pm = _prompts_for(task)
        if iteration == 0:
            label = "Fix" if task.get("type") == "bug" else "Implement"
            print(f"\n[{label}] '{task['id']}'")
            prompt = pm.build_implement_prompt(task, critic_feedback, revert_context)
        else:
            print(f"\n[Ralph Loop] Fix attempt {iteration}/{max_iterations}")
            prompt = pm.build_fix_prompt(task, errors, iteration)

        rc, _ = claude.run_claude(prompt, project_dir)
        if rc != 0:
            print(f"  [!] claude exited with code {rc}")

        print(f"\n[Tests]  {test_cmd}")
        passed, test_output = runner.run_tests(test_cmd, project_dir)

        if passed:
            print(f"  [OK] Tests passed in {iteration + 1} attempt(s)")
            return True

        fail_count = runner.extract_failure_count(test_output)
        count_str  = str(fail_count) if fail_count is not None else "?"
        print(f"  [FAIL] {count_str} failure(s)")

        if iteration == max_iterations:
            print(f"  [STOP] Max iterations ({max_iterations}) reached")
            break

        # ── Exit criterion 1: output unchanged ───────────────────
        if test_output == prev_output:
            print("  [STOP] Output identical to previous iteration — stuck")
            break

        # ── Exit criterion 2: no numeric progress ─────────────────
        if fail_count is not None and fail_count == prev_fail_count:
            stuck_streak += 1
            if stuck_streak >= STUCK_STREAK_THRESHOLD:
                print(f"  [STOP] Failure count stuck at {fail_count} for "
                      f"{stuck_streak + 1} iterations — conceptually stuck")
                break
        else:
            stuck_streak = 0

        # ── Exit criterion 3: regression ──────────────────────────
        if fail_count is not None and prev_fail_count is not None \
                and fail_count > prev_fail_count:
            print(f"  [STOP] Regression — {fail_count} failures (was {prev_fail_count})")
            break

        prev_output     = test_output
        prev_fail_count = fail_count

        errors = test_output[-MAX_ERROR_CHARS:] if len(test_output) > MAX_ERROR_CHARS \
            else test_output
        short = errors[:500].replace("\n", " ")
        print(f"  Errors: {short}{'...' if len(errors) > 500 else ''}")

    return False


def critic_loop(
    task: dict,
    test_cmd: str,
    project_dir: str,
    max_ralph_iterations: int,
    max_critic_iterations: int,
    revert_context: str | None = None,
    task_index: int = 0,
    total_tasks: int = 1,
    stats_out: dict | None = None,
) -> bool:
    """Outer solution-quality loop — Option-H sequential DoD gates
    (backlog item 028).

    Per design cycle:
        Phase 1  ralph_loop        (impl + test, iterated until green)
        Phase 2  struktur_check    (binary reviewer gate)
        Phase 3  docs_write        (actor updates mandatory docs)
        Phase 4  final_approval    (3-way reviewer; approve / docs / design)

    Backward routing:
        struktur fail            → next design cycle (Phase 1) with feedback
        docs escape              → next design cycle (Phase 1) with feedback
        final_approval "docs"    → repeat Phase 3 (up to MAX_DOCS_CYCLES);
                                   on cycle exhaust, force route to design
        final_approval "design"  → next design cycle (Phase 1) with feedback

    ``revert_context`` is forwarded to the first ``ralph_loop`` call only,
    so Claude knows a previous commit was rolled back and why (REQ-24).

    Returns True iff Phase 4 approves within the cycle budget.
    """
    task_start = time.time()
    print(f"\n{'='*64}")
    print(f"  TASK {task_index}/{total_tasks}: {task['id']}")
    print(f"{'='*64}")

    status.update_task_status(project_dir, task["id"], "in progress")

    def _finish(passed: bool, design_cycles: int, reason: str) -> bool:
        secs    = time.time() - task_start
        elapsed = prompts.format_elapsed(secs)
        if stats_out is not None:
            stats_out.update({"elapsed": secs, "design_cycles": design_cycles, "reason": reason})
        status.update_task_status(
            project_dir, task["id"], "done" if passed else "action needed",
        )
        symbol = "[✓]" if passed else "[✗]"
        state_str = "PASSED" if passed else "FAILED"
        cycles = (f"design: {design_cycles} cycle{'s' if design_cycles != 1 else ''}"
                  if design_cycles else "—")
        print(f"\n  {symbol} {task['id']} — {state_str}  ({elapsed})  [{cycles}]")
        return passed

    # Per-task test discovery (REQ-0008): grep TEST-*.md for **Task:** header.
    # docs/tests/index.md is a human aggregation and MUST NOT be parsed here.
    test_docs = tasks.find_test_docs_for_task(task, project_dir)
    if not test_docs:
        print(f"  [ERROR] No test specs found for '{task['id']}' —"
              f" expected at least one docs/tests/TEST-*.md file with"
              f" **Task:** header containing this task's ID (coverage gap).")
        return _finish(False, 0, "no test specs (coverage gap)")

    print(f"  [Check] Discovered {len(test_docs)} test spec(s) for '{task['id']}':")
    for p in test_docs:
        print(f"          - {p.name}")

    # Concatenate all discovered test-spec contents into a single string that
    # write_tests_phase() passes to Claude. Separator lets Claude visually
    # split the specs when multiple TEST files apply to the same task.
    test_doc_content = "\n\n---\n\n".join(
        p.read_text(encoding="utf-8") for p in test_docs
    )

    # Write tests once before any implementation attempt (REQ-30)
    task_test_cmd, ok = write_tests_phase(task, test_cmd, test_doc_content, project_dir)
    if not ok:
        return _finish(False, 0, "no tests written")

    critic_feedback: str | None = None
    prev_weaknesses: str | None = None

    for design_iter in range(max_critic_iterations + 1):
        if design_iter > 0:
            print(f"\n[Design Cycle] {design_iter}/{max_critic_iterations}")

        # ── Phase 1: Ralph (impl + test) ────────────────────────
        passed = ralph_loop(
            task, task_test_cmd, project_dir, max_ralph_iterations,
            critic_feedback,
            revert_context if design_iter == 0 else None,
        )
        if not passed:
            print("  [STOP] Could not get tests to pass — aborting")
            return _finish(False, design_iter, "tests failed")

        # ── Phase 2: Struktur-Check (binary gate) ───────────────
        print("\n[Struktur-Check] Reviewing solution structure...")
        _, struktur_output = claude.run_claude(
            _prompts_for(task).build_struktur_check_prompt(task), project_dir,
        )
        struktur_passed, struktur_reason = prompts.parse_struktur_check_output(struktur_output)

        if not struktur_passed:
            print(f"  [REJECT] Struktur: {struktur_reason}")
            new_feedback = f"structure: {struktur_reason}"
            if design_iter == max_critic_iterations:
                print(f"  [STOP] Max design cycles ({max_critic_iterations}) reached")
                return _finish(False, design_iter + 1, "design: max cycles")
            if new_feedback == prev_weaknesses:
                print("  [STOP] Reviewer repeating identical feedback — conceptually stuck")
                return _finish(False, design_iter + 1, "design: stuck")
            prev_weaknesses = new_feedback
            critic_feedback = new_feedback
            continue

        print(f"  [OK] {struktur_reason or 'structure sound'}")

        # ── Phases 3+4: Docs-Write → Final-Approval (inner cycle) ──
        docs_feedback: str | None = None
        design_feedback: str | None = None

        for docs_cycle in range(1, MAX_DOCS_CYCLES + 1):
            print(f"\n[Docs-Write] Cycle {docs_cycle}/{MAX_DOCS_CYCLES}")
            docs_prompt = _prompts_for(task).build_docs_write_prompt(
                task, MANDATORY_DOC_FILES,
            )
            if docs_feedback:
                docs_prompt = (
                    f"## Previous docs review feedback\n{docs_feedback}\n\n"
                    f"{docs_prompt}"
                )
            _, docs_output = claude.run_claude(docs_prompt, project_dir)
            docs_status, docs_reason = prompts.parse_docs_write_output(docs_output)

            if docs_status == "design_issue":
                print(f"  [ESCAPE] Docs actor: {docs_reason}")
                design_feedback = f"design_issue_from_docs_attempt: {docs_reason}"
                break

            # Constant one-liner so the progress log shows the phase
            # completed even though the actor produces no verdict on the
            # happy path. Content-aware summary is deferred (item 031).
            print("  [OK] docs updated")

            # Phase 4
            print("\n[Final-Approval] Reviewing full change (code+tests+docs)...")
            _, final_output = claude.run_claude(
                _prompts_for(task).build_final_approval_prompt(task, MANDATORY_DOC_FILES),
                project_dir,
            )
            verdict, criterion, final_reason = prompts.parse_final_approval_output(final_output)

            if verdict == "approve":
                print(f"  [OK] {final_reason or 'approved'}")
                return _finish(True, design_iter + 1, "passed")

            print(f"  [REJECT] route_to={verdict}"
                  f"{f', criterion={criterion}' if criterion else ''}: {final_reason}")

            if verdict == "docs":
                # Guardrail 3 (item 028): repeated docs failure ⇒ design issue.
                if docs_cycle >= MAX_DOCS_CYCLES:
                    print(f"  [ESCALATE] MAX_DOCS_CYCLES={MAX_DOCS_CYCLES} — forcing design route")
                    design_feedback = (
                        f"docs cycle escalation ({criterion or 'unspecified'}): {final_reason}"
                    )
                    break
                docs_feedback = f"{criterion or 'unspecified'}: {final_reason}"
                continue

            # verdict == "design"
            design_feedback = f"{criterion or 'unspecified'}: {final_reason}"
            break

        # Docs loop ended without approve → route back through Ralph.
        if design_iter == max_critic_iterations:
            print(f"  [STOP] Max design cycles ({max_critic_iterations}) reached")
            return _finish(False, design_iter + 1, "design: max cycles")
        if design_feedback == prev_weaknesses:
            print("  [STOP] Reviewer repeating identical feedback — conceptually stuck")
            return _finish(False, design_iter + 1, "design: stuck")
        prev_weaknesses = design_feedback
        critic_feedback = design_feedback

    return _finish(False, max_critic_iterations + 1, "unknown")
