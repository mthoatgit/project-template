"""
Tests for orchestrator.py

Each test references the requirement ID(s) it covers (REQ-NN).
Requirements without a test here are marked [no test] in the
REQUIREMENTS block in orchestrator.py.

run with:  pytest test_orchestrator.py -v
"""

import json

import pytest
from unittest.mock import MagicMock, call, patch


def _mock_popen(returncode=0, output=""):
    """Return a mock subprocess.Popen object whose stdout yields ``output`` line by line."""
    mock = MagicMock()
    mock.stdout = iter(output.splitlines(keepends=True))
    mock.returncode = returncode
    return mock

from orchestrator import (
    build_implement_prompt,
    build_task_test_cmd,
    build_write_tests_prompt,
    critic_loop,
    detect_task_test_files,
    extract_failure_count,
    find_test_doc,
    get_completed_task_ids,
    get_last_orchestrator_task_id,
    GIT_COMMIT_PREFIX,
    git_commit_task,
    git_reset_hard,
    load_tasks,
    parse_critic_output,
    ralph_loop,
    resume_check,
    STUCK_STREAK_THRESHOLD,
    update_task_status,
    write_tests_phase,
)

TASK = {"id": "T01-test", "content": "Implement foo", "path": "tasks/T01.md"}


# ─────────────────────────────────────────────────────────────
#  REQ-01  directory of .md files — all loaded, _TEMPLATE skipped
#  REQ-02  single .md file
#  REQ-03  .json file
#  REQ-04  .yaml / .yml file
# ─────────────────────────────────────────────────────────────

def test_load_tasks_from_directory(tmp_path):  # REQ-01
    (tmp_path / "T01-foo.md").write_text("content foo", encoding="utf-8")
    (tmp_path / "T02-bar.md").write_text("content bar", encoding="utf-8")

    tasks = load_tasks(str(tmp_path))

    assert len(tasks) == 2
    ids = [t["id"] for t in tasks]
    assert "T01-foo" in ids
    assert "T02-bar" in ids


def test_load_tasks_from_directory_skips_template(tmp_path):  # REQ-01
    (tmp_path / "T01-real.md").write_text("real content", encoding="utf-8")
    (tmp_path / "_TEMPLATE.md").write_text("template content", encoding="utf-8")

    tasks = load_tasks(str(tmp_path))

    assert len(tasks) == 1
    assert tasks[0]["id"] == "T01-real"


def test_load_tasks_from_directory_sorted(tmp_path):  # REQ-01
    (tmp_path / "T03-last.md").write_text("c", encoding="utf-8")
    (tmp_path / "T01-first.md").write_text("a", encoding="utf-8")
    (tmp_path / "T02-middle.md").write_text("b", encoding="utf-8")

    tasks = load_tasks(str(tmp_path))

    assert [t["id"] for t in tasks] == ["T01-first", "T02-middle", "T03-last"]


def test_load_tasks_from_single_md_file(tmp_path):  # REQ-02
    f = tmp_path / "T05-task.md"
    f.write_text("# My Task\nDo something.", encoding="utf-8")

    tasks = load_tasks(str(f))

    assert len(tasks) == 1
    assert tasks[0]["id"] == "T05-task"
    assert "Do something." in tasks[0]["content"]


def test_load_tasks_from_json_list(tmp_path):  # REQ-03
    data = [
        {"id": "T01", "content": "first"},
        {"id": "T02", "content": "second"},
    ]
    f = tmp_path / "tasks.json"
    f.write_text(json.dumps(data), encoding="utf-8")

    tasks = load_tasks(str(f))

    assert len(tasks) == 2
    assert tasks[0]["id"] == "T01"
    assert tasks[1]["content"] == "second"


def test_load_tasks_from_json_single_object(tmp_path):  # REQ-03
    data = {"id": "T01", "content": "only task"}
    f = tmp_path / "tasks.json"
    f.write_text(json.dumps(data), encoding="utf-8")

    tasks = load_tasks(str(f))

    assert len(tasks) == 1
    assert tasks[0]["id"] == "T01"


def test_load_tasks_from_yaml(tmp_path):  # REQ-04
    yaml = pytest.importorskip("yaml")
    data = [{"id": "T01", "content": "yaml task"}]
    f = tmp_path / "tasks.yaml"
    f.write_text(yaml.dump(data), encoding="utf-8")

    tasks = load_tasks(str(f))

    assert len(tasks) == 1
    assert tasks[0]["id"] == "T01"
    assert tasks[0]["content"] == "yaml task"


def test_load_tasks_from_yml_extension(tmp_path):  # REQ-04
    yaml = pytest.importorskip("yaml")
    data = [{"id": "T02", "content": "yml task"}]
    f = tmp_path / "tasks.yml"
    f.write_text(yaml.dump(data), encoding="utf-8")

    tasks = load_tasks(str(f))

    assert len(tasks) == 1
    assert tasks[0]["id"] == "T02"


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
#  REQ-08  passes on first attempt
#  REQ-09  passes after fix attempt
# ─────────────────────────────────────────────────────────────

@patch("orchestrator.run_tests")
@patch("orchestrator.run_claude")
def test_passes_on_first_attempt(mock_claude, mock_tests):  # REQ-08
    mock_claude.return_value = (0, "implemented")
    mock_tests.return_value  = (True, "1 passed in 0.1s")

    assert ralph_loop(TASK, "pytest", "/project", max_iterations=5) is True
    assert mock_claude.call_count == 1
    assert mock_tests.call_count  == 1


@patch("orchestrator.run_tests")
@patch("orchestrator.run_claude")
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

@patch("orchestrator.run_tests")
@patch("orchestrator.run_claude")
def test_exit_identical_output(mock_claude, mock_tests):  # REQ-10
    mock_claude.return_value = (0, "")
    mock_tests.return_value  = (False, "3 failed, AssertionError")

    assert ralph_loop(TASK, "pytest", "/project", max_iterations=5) is False
    assert mock_tests.call_count == 2  # iter 0 sets baseline, iter 1 matches → stop


# ─────────────────────────────────────────────────────────────
#  REQ-11  criterion 2 — stuck streak
#  REQ-12  criterion 2 — streak resets on progress
# ─────────────────────────────────────────────────────────────

@patch("orchestrator.run_tests")
@patch("orchestrator.run_claude")
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


@patch("orchestrator.run_tests")
@patch("orchestrator.run_claude")
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

@patch("orchestrator.run_tests")
@patch("orchestrator.run_claude")
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

@patch("orchestrator.run_tests")
@patch("orchestrator.run_claude")
def test_exit_max_iterations(mock_claude, mock_tests):  # REQ-14
    max_iter = 3
    mock_claude.return_value = (0, "incremental fix")
    mock_tests.side_effect = [
        (False, f"{10 - i} failed, iteration {i}") for i in range(max_iter + 1)
    ]

    assert ralph_loop(TASK, "pytest", "/project", max_iterations=max_iter) is False
    assert mock_tests.call_count == max_iter + 1


# ─────────────────────────────────────────────────────────────
#  REQ-15  critic runs after tests pass
#  REQ-16  critic evaluates design, not formatting  (verified via prompt content)
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


def test_build_critic_prompt_covers_design_not_style():  # REQ-16
    from orchestrator import build_critic_prompt
    prompt = build_critic_prompt(TASK)
    assert "design" in prompt.lower() or "pattern" in prompt.lower()
    assert "Do NOT evaluate" in prompt
    assert "formatting" in prompt.lower() or "indentation" in prompt.lower()


@patch("orchestrator.run_tests")
@patch("orchestrator.run_claude")
def test_critic_runs_after_tests_pass(mock_claude, mock_tests):  # REQ-15
    # First call: implementation; second call: critic review
    mock_claude.side_effect = [
        (0, "implemented"),           # ralph_loop: implement
        (0, "APPROVED — clean"),      # critic review
    ]
    mock_tests.return_value = (True, "1 passed")

    result = critic_loop(TASK, "pytest", "/project", max_ralph_iterations=5, max_critic_iterations=3)

    assert result is True
    assert mock_claude.call_count == 2  # implement + critic


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


def task_content_present(prompt: str) -> bool:
    return TASK["content"] in prompt


@patch("orchestrator.run_tests")
@patch("orchestrator.run_claude")
def test_critic_rejection_triggers_reimplementation_with_feedback(mock_claude, mock_tests):  # REQ-18
    weakness = "- Uses procedural style instead of appropriate OOP pattern"
    mock_claude.side_effect = [
        (0, "first implementation"),           # cycle 1: implement
        (0, f"REJECTED\n{weakness}"),          # cycle 1: critic rejects
        (0, "second implementation"),          # cycle 2: re-implement
        (0, "APPROVED — now uses OOP"),        # cycle 2: critic approves
    ]
    mock_tests.return_value = (True, "all passed")

    result = critic_loop(TASK, "pytest", "/project", max_ralph_iterations=5, max_critic_iterations=3)

    assert result is True
    # The third claude call (re-implementation) must include critic feedback
    third_call_prompt = mock_claude.call_args_list[2][0][0]
    assert weakness in third_call_prompt


# ─────────────────────────────────────────────────────────────
#  REQ-19  critic stuck detection — same feedback twice
# ─────────────────────────────────────────────────────────────

@patch("orchestrator.run_tests")
@patch("orchestrator.run_claude")
def test_critic_loop_aborts_on_repeated_feedback(mock_claude, mock_tests):  # REQ-19
    weakness = "- Wrong abstraction level throughout"
    mock_claude.side_effect = [
        (0, "implementation v1"),       # cycle 1: implement
        (0, f"REJECTED\n{weakness}"),   # cycle 1: critic rejects
        (0, "implementation v2"),       # cycle 2: re-implement
        (0, f"REJECTED\n{weakness}"),   # cycle 2: same feedback → stuck
    ]
    mock_tests.return_value = (True, "all passed")

    result = critic_loop(TASK, "pytest", "/project", max_ralph_iterations=5, max_critic_iterations=3)

    assert result is False
    assert mock_claude.call_count == 4


# ─────────────────────────────────────────────────────────────
#  REQ-20  critic loop max iterations
# ─────────────────────────────────────────────────────────────

@patch("orchestrator.run_tests")
@patch("orchestrator.run_claude")
def test_critic_loop_max_iterations(mock_claude, mock_tests):  # REQ-20
    max_critic = 2
    mock_claude.side_effect = [
        (0, f"implementation {i // 2}") if i % 2 == 0
        else (0, f"REJECTED\n- concern {i}")   # different feedback each time
        for i in range((max_critic + 1) * 2)
    ]
    mock_tests.return_value = (True, "all passed")

    result = critic_loop(TASK, "pytest", "/project", max_ralph_iterations=5,
                         max_critic_iterations=max_critic)

    assert result is False
    # implement + critic per cycle, cycles = max_critic + 1
    assert mock_claude.call_count == (max_critic + 1) * 2


@patch("orchestrator.run_tests")
@patch("orchestrator.run_claude")
def test_critic_loop_fails_if_ralph_loop_fails(mock_claude, mock_tests):  # REQ-20
    mock_claude.return_value = (0, "")
    mock_tests.return_value = (False, "3 failed, identical every time")

    result = critic_loop(TASK, "pytest", "/project", max_ralph_iterations=5, max_critic_iterations=3)

    assert result is False


# ─────────────────────────────────────────────────────────────
#  REQ-21  git_commit_task: stage all changes and commit
# ─────────────────────────────────────────────────────────────

@patch("orchestrator.subprocess.run")
def test_git_commit_task_stages_and_commits(mock_run):  # REQ-21
    mock_run.side_effect = [
        MagicMock(returncode=0),                                          # git add -A
        MagicMock(returncode=0, stdout="1 file changed", stderr=""),      # git commit
    ]

    result = git_commit_task("T01-foo", "/project")

    assert result is True
    assert mock_run.call_count == 2
    add_cmd = mock_run.call_args_list[0][0][0]
    assert add_cmd == ["git", "add", "-A"]
    commit_cmd = mock_run.call_args_list[1][0][0]
    assert commit_cmd[:2] == ["git", "commit"]
    commit_msg = commit_cmd[3]
    assert "T01-foo" in commit_msg
    assert GIT_COMMIT_PREFIX in commit_msg


@patch("orchestrator.subprocess.run")
def test_git_commit_task_returns_false_on_git_failure(mock_run):  # REQ-21
    mock_run.side_effect = [
        MagicMock(returncode=0),                                          # git add -A
        MagicMock(returncode=1, stdout="", stderr="nothing to commit"),   # git commit fails
    ]

    result = git_commit_task("T01-foo", "/project")

    assert result is False


# ─────────────────────────────────────────────────────────────
#  REQ-22  get_completed_task_ids: parse git log for orchestrator commits
# ─────────────────────────────────────────────────────────────

@patch("orchestrator.subprocess.run")
def test_get_completed_task_ids_parses_log(mock_run):  # REQ-22
    mock_run.return_value = MagicMock(returncode=0, stdout=(
        "abc1234 [orchestrator] T01-alpha — tests pass, design approved\n"
        "def5678 [orchestrator] T02-beta — tests pass, design approved\n"
    ))

    ids = get_completed_task_ids("/project")

    assert ids == ["T01-alpha", "T02-beta"]


@patch("orchestrator.subprocess.run")
def test_get_completed_task_ids_empty_when_no_prior_commits(mock_run):  # REQ-22
    mock_run.return_value = MagicMock(returncode=0, stdout="")

    ids = get_completed_task_ids("/project")

    assert ids == []


# ─────────────────────────────────────────────────────────────
#  REQ-22  get_last_orchestrator_task_id: most recent orchestrator task
# ─────────────────────────────────────────────────────────────

@patch("orchestrator.subprocess.run")
def test_get_last_orchestrator_task_id_returns_id(mock_run):  # REQ-22
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout="abc1234 [orchestrator] T02-beta — tests pass, design approved\n",
    )

    task_id = get_last_orchestrator_task_id("/project")

    assert task_id == "T02-beta"


@patch("orchestrator.subprocess.run")
def test_get_last_orchestrator_task_id_returns_none_when_no_commits(mock_run):  # REQ-22
    mock_run.return_value = MagicMock(returncode=0, stdout="")

    task_id = get_last_orchestrator_task_id("/project")

    assert task_id is None


# ─────────────────────────────────────────────────────────────
#  REQ-24  git_reset_hard: removes last commit via git reset --hard HEAD~1
# ─────────────────────────────────────────────────────────────

@patch("orchestrator.subprocess.run")
def test_git_reset_hard_calls_correct_command(mock_run):  # REQ-24
    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

    result = git_reset_hard("/project")

    assert result is True
    call_args = mock_run.call_args
    assert call_args[0][0] == ["git", "reset", "--hard", "HEAD~1"]
    assert call_args[1]["cwd"] == "/project"


# ─────────────────────────────────────────────────────────────
#  REQ-23  resume_check: no prior commits → all tasks, no revert context
# ─────────────────────────────────────────────────────────────

_RESUME_TASKS = [
    {"id": "T01-alpha", "content": "task alpha"},
    {"id": "T02-beta",  "content": "task beta"},
]


@patch("orchestrator.get_completed_task_ids")
def test_resume_check_no_prior_commits_returns_all(mock_ids):  # REQ-23
    mock_ids.return_value = []

    remaining, context = resume_check(_RESUME_TASKS, "pytest", "/project")

    assert remaining == _RESUME_TASKS
    assert context is None


@patch("orchestrator.run_tests")
@patch("orchestrator.get_completed_task_ids")
def test_resume_check_green_tests_skip_completed(mock_ids, mock_tests):  # REQ-23
    mock_ids.return_value = ["T01-alpha"]
    mock_tests.return_value = (True, "2 passed")

    remaining, context = resume_check(_RESUME_TASKS, "pytest", "/project")

    assert len(remaining) == 1
    assert remaining[0]["id"] == "T02-beta"
    assert context is None


# ─────────────────────────────────────────────────────────────
#  REQ-24  resume_check: failing tests → reset last commit, return context
# ─────────────────────────────────────────────────────────────

@patch("orchestrator.git_reset_hard")
@patch("orchestrator.get_last_orchestrator_task_id")
@patch("orchestrator.run_tests")
@patch("orchestrator.get_completed_task_ids")
def test_resume_check_failing_tests_resets_and_returns_context(
    mock_ids, mock_tests, mock_last_id, mock_reset,
):  # REQ-24
    mock_ids.return_value = ["T01-alpha", "T02-beta"]
    mock_tests.return_value = (False, "3 failed in 0.5s")
    mock_last_id.return_value = "T02-beta"
    mock_reset.return_value = True

    remaining, context = resume_check(_RESUME_TASKS, "pytest", "/project")

    mock_reset.assert_called_once_with("/project")
    assert any(t["id"] == "T02-beta" for t in remaining)
    assert context is not None
    assert "rolled back" in context.lower()
    assert "3 failed" in context


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
#  REQ-25  task marked failed if retry with revert context still cannot fix
# ─────────────────────────────────────────────────────────────

@patch("orchestrator.run_tests")
@patch("orchestrator.run_claude")
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
#  REQ-21  main() commits after each successfully completed task
# ─────────────────────────────────────────────────────────────

@patch("orchestrator.run_tests")
@patch("orchestrator.git_commit_task")
@patch("orchestrator.critic_loop")
@patch("orchestrator.resume_check")
@patch("orchestrator.find_test_doc")
@patch("orchestrator.load_tasks")
def test_main_commits_after_each_successful_task(
    mock_load, mock_find_doc, mock_resume, mock_critic, mock_commit, mock_tests, tmp_path,
):  # REQ-21
    from orchestrator import main
    from unittest.mock import MagicMock
    task_a = {"id": "T01-alpha", "content": "alpha"}
    task_b = {"id": "T02-beta",  "content": "beta"}
    mock_load.return_value = [task_a, task_b]
    mock_doc = MagicMock()
    mock_doc.name = "E1-test.md"
    mock_doc.read_text.return_value = "# Test Design"
    mock_find_doc.return_value = mock_doc
    mock_resume.return_value = ([task_a, task_b], None)
    mock_critic.return_value = True
    mock_commit.return_value = True
    mock_tests.return_value = (True, "all passed")

    with patch("sys.argv", [
        "orchestrator.py", "--tasks", "docs/tasks/epics/E1/",
        "--test-cmd", "pytest",
        "--project-dir", str(tmp_path),
    ]):
        with pytest.raises(SystemExit):
            main()

    assert mock_commit.call_count == 2
    committed_ids = [c[0][0] for c in mock_commit.call_args_list]
    assert "T01-alpha" in committed_ids
    assert "T02-beta"  in committed_ids


# ─────────────────────────────────────────────────────────────
#  REQ-26  run_tests uses PowerShell on Windows, system shell elsewhere
# ─────────────────────────────────────────────────────────────

@patch("orchestrator.subprocess.Popen")
@patch("orchestrator.platform.system")
def test_run_tests_uses_powershell_on_windows(mock_system, mock_popen):  # REQ-26
    from orchestrator import run_tests
    mock_system.return_value = "Windows"
    mock_popen.return_value = _mock_popen(returncode=0, output="1 passed\n")

    run_tests("pytest", "/project")

    call_args = mock_popen.call_args
    assert call_args[0][0] == ["powershell", "-NoProfile", "-Command", "pytest"]
    assert call_args[1].get("shell") is False


@patch("orchestrator.subprocess.Popen")
@patch("orchestrator.platform.system")
def test_run_tests_uses_shell_on_linux(mock_system, mock_popen):  # REQ-26
    from orchestrator import run_tests
    mock_system.return_value = "Linux"
    mock_popen.return_value = _mock_popen(returncode=0, output="1 passed\n")

    run_tests("pytest", "/project")

    call_args = mock_popen.call_args
    assert call_args[0][0] == "pytest"
    assert call_args[1].get("shell") is True


# ─────────────────────────────────────────────────────────────
#  REQ-27  run_claude passes --dangerously-skip-permissions
# ─────────────────────────────────────────────────────────────

@patch("orchestrator.subprocess.Popen")
def test_run_claude_passes_dangerously_skip_permissions(mock_popen):  # REQ-27
    from orchestrator import run_claude
    mock_popen.return_value = _mock_popen(returncode=0, output="done\n")

    run_claude("implement this", "/project")

    cmd = mock_popen.call_args[0][0]
    assert "--dangerously-skip-permissions" in cmd
    assert "-p" in cmd
    assert "implement this" in cmd


# ─────────────────────────────────────────────────────────────
#  REQ-28  session-limit detection and auto-resume
# ─────────────────────────────────────────────────────────────

def test_parse_reset_time_returns_none_for_unparseable():  # REQ-28
    from orchestrator import parse_reset_time
    assert parse_reset_time("some unrelated error") is None


def test_parse_reset_time_returns_future_datetime():  # REQ-28
    from orchestrator import parse_reset_time
    from datetime import datetime
    msg = "You've hit your session limit · resets 11:40am (Europe/Berlin)"
    result = parse_reset_time(msg)
    assert result is not None
    now = datetime.now(result.tzinfo) if result.tzinfo else datetime.now()
    assert result > now


@patch("orchestrator.subprocess.Popen")
@patch("orchestrator.handle_session_limit")
def test_run_claude_detects_session_limit_and_retries(mock_handle, mock_popen):  # REQ-28
    from orchestrator import run_claude
    limit_msg = "You've hit your session limit · resets 11:40am (Europe/Berlin)\n"
    mock_popen.side_effect = [
        _mock_popen(returncode=1, output=limit_msg),
        _mock_popen(returncode=0, output="done\n"),
    ]
    rc, output = run_claude("implement this", "/project")
    assert mock_handle.call_count == 1
    assert rc == 0
    assert output == "done"


@patch("orchestrator.sys.exit")
@patch("orchestrator.parse_reset_time", return_value=None)
def test_handle_session_limit_exits_2_when_unparseable(mock_parse, mock_exit):  # REQ-28
    from orchestrator import handle_session_limit
    handle_session_limit("session limit hit, no time info")
    mock_exit.assert_called_once_with(2)


# ─────────────────────────────────────────────────────────────
#  REQ-29  find_test_doc: locate and validate Epic test design doc
# ─────────────────────────────────────────────────────────────

def test_find_test_doc_returns_path_when_found(tmp_path):  # REQ-29
    doc = tmp_path / "docs" / "tests" / "epics"
    doc.mkdir(parents=True)
    (doc / "E1-tests.md").write_text("# Test Design\nsome scenarios", encoding="utf-8")

    result = find_test_doc("docs/tasks/epics/E1/", str(tmp_path))

    assert result.name == "E1-tests.md"


def test_find_test_doc_exits_when_missing(tmp_path):  # REQ-29
    (tmp_path / "docs" / "tests" / "epics").mkdir(parents=True)

    with pytest.raises(SystemExit):
        find_test_doc("docs/tasks/epics/E1/", str(tmp_path))


def test_find_test_doc_exits_when_template(tmp_path):  # REQ-29
    doc_dir = tmp_path / "docs" / "tests" / "epics"
    doc_dir.mkdir(parents=True)
    (doc_dir / "E1-tests.md").write_text(
        "---\nstatus: template\n---\n# Test Design", encoding="utf-8"
    )

    with pytest.raises(SystemExit):
        find_test_doc("docs/tasks/epics/E1/", str(tmp_path))


def test_find_test_doc_exits_when_no_epic_in_path(tmp_path):  # REQ-29
    with pytest.raises(SystemExit):
        find_test_doc(str(tmp_path / "some" / "flat" / "tasks.json"), str(tmp_path))


# ─────────────────────────────────────────────────────────────
#  REQ-30  build_write_tests_prompt: forbids stubs and production code
# ─────────────────────────────────────────────────────────────

def test_build_write_tests_prompt_contains_task_and_doc():  # REQ-30
    prompt = build_write_tests_prompt(TASK, "# Scenarios\n- scenario A")

    assert TASK["id"] in prompt
    assert TASK["content"] in prompt
    assert "# Scenarios" in prompt
    assert "assert False" in prompt      # explicitly forbidden
    assert "NotImplementedError" in prompt
    assert "production" in prompt.lower() or "source" in prompt.lower()


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


# ─────────────────────────────────────────────────────────────
#  REQ-33  build_task_test_cmd: scopes test command to specific files
# ─────────────────────────────────────────────────────────────

@pytest.mark.parametrize("test_cmd, files, expected_contains", [
    ("pytest tests/",          ["tests/test_config.py"], "tests/test_config.py"),
    ("python -m pytest tests/",["tests/test_model.py"],  "tests/test_model.py"),
    ("pytest",                 ["tests/test_foo.py"],    "tests/test_foo.py"),
])
def test_build_task_test_cmd_scopes_to_files(test_cmd, files, expected_contains):  # REQ-33
    result = build_task_test_cmd(test_cmd, files)

    assert expected_contains in result
    assert "tests/" not in result.replace(expected_contains, "")


# ─────────────────────────────────────────────────────────────
#  REQ-31  write_tests_phase: fails task when no files created
# ─────────────────────────────────────────────────────────────

@patch("orchestrator.detect_task_test_files", return_value=[])
@patch("orchestrator.run_claude", return_value=(0, "wrote nothing"))
def test_write_tests_phase_fails_when_no_files_created(mock_claude, mock_detect):  # REQ-31
    cmd, ok = write_tests_phase(TASK, "pytest tests/", "# doc", "/project")

    assert ok is False
    assert cmd == "pytest tests/"  # original cmd returned unchanged


# ─────────────────────────────────────────────────────────────
#  REQ-34  main() runs final verification after all tasks
# ─────────────────────────────────────────────────────────────

@patch("orchestrator.run_tests")
@patch("orchestrator.git_commit_task")
@patch("orchestrator.critic_loop")
@patch("orchestrator.resume_check")
@patch("orchestrator.find_test_doc")
@patch("orchestrator.load_tasks")
def test_main_runs_final_verification(
    mock_load, mock_find_doc, mock_resume, mock_critic, mock_commit, mock_tests, tmp_path,
):  # REQ-34
    from orchestrator import main
    task_a = {"id": "T01-alpha", "content": "alpha"}
    mock_load.return_value = [task_a]
    mock_doc = MagicMock()
    mock_doc.name = "E1-test.md"
    mock_doc.read_text.return_value = "# Test Design"
    mock_find_doc.return_value = mock_doc
    mock_resume.return_value = ([task_a], None)
    mock_critic.return_value = True
    mock_commit.return_value = True
    mock_tests.return_value = (True, "all passed")

    with patch("sys.argv", [
        "orchestrator.py", "--tasks", "docs/tasks/epics/E1/",
        "--test-cmd", "pytest",
        "--project-dir", str(tmp_path),
    ]):
        with pytest.raises(SystemExit) as exc_info:
            main()

    assert mock_tests.call_count == 1  # final verification ran
    assert exc_info.value.code == 0


# ─────────────────────────────────────────────────────────────
#  REQ-38  update_task_status rewrites docs/tasks/index.md
# ─────────────────────────────────────────────────────────────

INDEX_SAMPLE = (
    "# Task Status\n"
    "\n"
    "| ID  | Epic | Title                  | Status        |\n"
    "|-----|------|------------------------|---------------|\n"
    "| T01 | E1   | Build and dependencies | pending       |\n"
    "| T02 | E1   | Docker compose stack   | pending       |\n"
)


def _make_index(tmp_path, body=INDEX_SAMPLE):
    (tmp_path / "docs" / "tasks").mkdir(parents=True)
    f = tmp_path / "docs" / "tasks" / "index.md"
    f.write_text(body, encoding="utf-8")
    return f


def _row_for(path, task_id):
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith(f"| {task_id} "):
            return line
    return None


def test_update_task_status_flips_pending_to_in_progress(tmp_path):  # REQ-38
    f = _make_index(tmp_path)

    assert update_task_status(str(tmp_path), "T01-build", "in progress") is True

    row = _row_for(f, "T01")
    assert "in progress" in row
    # pipe positions unchanged (status padded to 13 chars = 'action needed')
    assert row.count("|") == 5
    assert "| in progress   |" in row
    # sibling row untouched
    assert "| T02 | E1   | Docker compose stack   | pending       |" in f.read_text(encoding="utf-8")


def test_update_task_status_matches_short_id_only(tmp_path):  # REQ-38
    f = _make_index(tmp_path)

    # passing just "T02" (no slug) must still find the row
    assert update_task_status(str(tmp_path), "T02", "done") is True
    assert "| done          |" in _row_for(f, "T02")


def test_update_task_status_can_flip_to_action_needed(tmp_path):  # REQ-38
    f = _make_index(tmp_path)

    assert update_task_status(str(tmp_path), "T01-build", "action needed") is True
    assert "| action needed |" in _row_for(f, "T01")


def test_update_task_status_preserves_column_alignment(tmp_path):  # REQ-38
    f = _make_index(tmp_path)

    # Every transition should preserve the pipe positions of the row.
    baseline_pipes = [i for i, c in enumerate(_row_for(f, "T01")) if c == "|"]
    for target in ("in progress", "done", "action needed", "pending"):
        update_task_status(str(tmp_path), "T01-build", target)
        pipes = [i for i, c in enumerate(_row_for(f, "T01")) if c == "|"]
        assert pipes == baseline_pipes, f"pipes shifted after writing {target!r}"


def test_update_task_status_missing_file_returns_false(tmp_path):  # REQ-38
    # no index.md created
    assert update_task_status(str(tmp_path), "T01-build", "done") is False


def test_update_task_status_unmatched_id_returns_false(tmp_path):  # REQ-38
    _make_index(tmp_path)
    assert update_task_status(str(tmp_path), "T99-nope", "done") is False


def test_update_task_status_rejects_invalid_status(tmp_path):  # REQ-38
    _make_index(tmp_path)
    with pytest.raises(ValueError):
        update_task_status(str(tmp_path), "T01-build", "wip")


@patch("orchestrator.update_task_status")
@patch("orchestrator.run_claude")
@patch("orchestrator.run_tests")
def test_critic_loop_flips_status_to_done_on_success(  # REQ-38
    mock_tests, mock_claude, mock_update, tmp_path,
):
    mock_tests.return_value = (True, "pytest: 3 passed")
    mock_claude.return_value = (0, "APPROVED — looks great")

    from orchestrator import critic_loop
    ok = critic_loop(TASK, "pytest", str(tmp_path), max_ralph_iterations=1, max_critic_iterations=1)

    assert ok is True
    calls = [c.args for c in mock_update.call_args_list]
    assert (str(tmp_path), TASK["id"], "in progress") in calls
    assert (str(tmp_path), TASK["id"], "done") in calls


@patch("orchestrator.update_task_status")
@patch("orchestrator.run_claude")
@patch("orchestrator.run_tests")
def test_critic_loop_flips_status_to_action_needed_on_failure(  # REQ-38
    mock_tests, mock_claude, mock_update, tmp_path,
):
    # tests never pass → ralph_loop returns False → critic_loop returns False
    mock_tests.return_value = (False, "pytest: 3 failed")
    mock_claude.return_value = (0, "")

    from orchestrator import critic_loop
    ok = critic_loop(TASK, "pytest", str(tmp_path), max_ralph_iterations=1, max_critic_iterations=1)

    assert ok is False
    calls = [c.args for c in mock_update.call_args_list]
    assert (str(tmp_path), TASK["id"], "in progress") in calls
    assert (str(tmp_path), TASK["id"], "action needed") in calls
