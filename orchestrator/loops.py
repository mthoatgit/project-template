"""The two nested loops that drive each task through TDD:

- ``ralph_loop``: inner correctness loop (implement → test → fix)
- ``critic_loop``: outer solution-quality loop (correctness + adversarial review)
- ``write_tests_phase``: pre-implementation test-writing step
"""
import time

# Module-attribute access (``runner.run_tests``, ``claude.run_claude``, ...)
# so @patch("orchestrator.runner.run_tests") etc. propagate into these
# callers — see docs/orchestrator-requirements.md.
from . import claude, prompts, runner, status
from .config import MAX_ERROR_CHARS, STUCK_STREAK_THRESHOLD


def write_tests_phase(
    task: dict,
    test_cmd: str,
    test_doc_content: str,
    project_dir: str,
) -> tuple[str, bool]:
    """Call Claude to write tests, then verify they fail (REQ-30, REQ-31, REQ-32)."""
    print(f"\n[Write Tests] '{task['id']}'")
    prompt = prompts.build_write_tests_prompt(task, test_doc_content)
    rc, _ = claude.run_claude(prompt, project_dir)
    if rc != 0:
        print(f"  [!] claude exited with code {rc}")

    test_files = runner.detect_task_test_files(project_dir)
    if not test_files:
        print("  [ERROR] No test files were created — aborting task")
        return test_cmd, False
    print(f"  Created: {', '.join(test_files)}")

    # Framework-agnostic: the project's --test-cmd runs *all* tests. New
    # tests are the only ones that should be failing at this point — if
    # the pre-run tree was green, a red run here means our new tests are
    # failing as expected.
    print(f"\n[Verify]  {test_cmd}")
    passed, verify_output = runner.run_tests(test_cmd, project_dir)
    if passed:
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
        if iteration == 0:
            print(f"\n[Implement] '{task['id']}'")
            prompt = prompts.build_implement_prompt(task, critic_feedback, revert_context)
        else:
            print(f"\n[Ralph Loop] Fix attempt {iteration}/{max_iterations}")
            prompt = prompts.build_fix_prompt(task, errors, iteration)

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
    test_doc_content: str | None = None,
    task_index: int = 0,
    total_tasks: int = 1,
    stats_out: dict | None = None,
) -> bool:
    """Outer loop: correctness via ``ralph_loop``, then design quality via
    the Critic.

    Runs ``ralph_loop`` to get tests green, then asks the Critic to
    evaluate the solution approach. If rejected, re-runs ``ralph_loop``
    with the Critic's feedback as context (but without the rejected code).
    Repeats until the Critic approves or an exit criterion fires.

    ``revert_context`` is forwarded to the first ``ralph_loop`` call only,
    so Claude knows a previous commit was rolled back and why (REQ-24).

    Returns True if tests pass AND Critic approves, False otherwise.
    """
    task_start = time.time()
    print(f"\n{'='*64}")
    print(f"  TASK {task_index}/{total_tasks}: {task['id']}")
    print(f"{'='*64}")

    status.update_task_status(project_dir, task["id"], "in progress")

    def _finish(passed: bool, critic_cycles: int, reason: str) -> bool:
        secs    = time.time() - task_start
        elapsed = prompts.format_elapsed(secs)
        if stats_out is not None:
            stats_out.update({"elapsed": secs, "critic_cycles": critic_cycles, "reason": reason})
        status.update_task_status(
            project_dir, task["id"], "done" if passed else "action needed",
        )
        symbol = "[✓]" if passed else "[✗]"
        state_str = "PASSED" if passed else "FAILED"
        cycles = (f"critic: {critic_cycles} cycle{'s' if critic_cycles != 1 else ''}"
                  if critic_cycles else "—")
        print(f"\n  {symbol} {task['id']} — {state_str}  ({elapsed})  [{cycles}]")
        return passed

    # Write tests once before any implementation attempt (REQ-30)
    task_test_cmd = test_cmd
    if test_doc_content is not None:
        task_test_cmd, ok = write_tests_phase(task, test_cmd, test_doc_content, project_dir)
        if not ok:
            return _finish(False, 0, "no tests written")

    critic_feedback: str | None = None
    prev_weaknesses: str | None = None

    for critic_iter in range(max_critic_iterations + 1):
        if critic_iter > 0:
            print(f"\n[Critic Loop] Re-implementation cycle "
                  f"{critic_iter}/{max_critic_iterations}")

        passed = ralph_loop(
            task, task_test_cmd, project_dir, max_ralph_iterations,
            critic_feedback,
            revert_context if critic_iter == 0 else None,
        )

        if not passed:
            print("  [STOP] Could not get tests to pass — aborting")
            return _finish(False, critic_iter, "tests failed")

        print(f"\n[Critic] Reviewing solution approach...")
        _, critic_output = claude.run_claude(prompts.build_critic_prompt(task), project_dir)
        approved, weaknesses = prompts.parse_critic_output(critic_output)

        if approved:
            first_line = critic_output.strip().splitlines()[0] if critic_output.strip() else ""
            print(f"  [OK] {first_line}")
            return _finish(True, critic_iter + 1, "passed")

        print(f"  [REJECT] Design concerns:")
        for line in weaknesses.splitlines()[:6]:
            if line.strip():
                print(f"    {line}")

        if critic_iter == max_critic_iterations:
            print(f"  [STOP] Max critic iterations ({max_critic_iterations}) reached")
            return _finish(False, critic_iter + 1, "critic: max cycles")

        if weaknesses == prev_weaknesses:
            print("  [STOP] Critic repeating identical feedback — conceptually stuck")
            return _finish(False, critic_iter + 1, "critic: stuck")

        prev_weaknesses = weaknesses
        critic_feedback = weaknesses

    return _finish(False, max_critic_iterations + 1, "unknown")
