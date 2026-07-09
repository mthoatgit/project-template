"""Orchestrator package — TDD implementation loop driver.

The single-file `orchestrator.py` was split into this package once it
crossed ~1500 lines. Everything the tests or external callers touch is
re-exported here so imports and mock-patch strings remain stable.

Requirements live in `docs/orchestrator-requirements.md`.
"""

# ── Stdlib re-exports needed for tests ─────────────────────────
# @patch("orchestrator.subprocess.Popen"), @patch("orchestrator.sys.exit")
# and similar mocks work because these names live on the orchestrator
# package. They also make it clear at a glance which stdlib bits the
# orchestrator leans on.
import subprocess  # noqa: F401
import platform    # noqa: F401
import sys         # noqa: F401

# ── Submodules — imported so ``orchestrator.<mod>.<name>`` mock
# paths (e.g. @patch("orchestrator.runner.run_tests")) resolve.
from . import config       # noqa: F401
from . import output       # noqa: F401
from . import tasks        # noqa: F401
from . import runner       # noqa: F401
from . import claude       # noqa: F401
from . import status       # noqa: F401
from . import prompts      # noqa: F401
from . import git_ops      # noqa: F401
from . import loops        # noqa: F401
from . import main as _main  # noqa: F401 — expose flat main() below

# ── Public API — flat access preserved from the pre-split layout ──
from .config import (
    MAX_ITERATIONS, STUCK_STREAK_THRESHOLD, MAX_CRITIC_ITERATIONS,
    MAX_ERROR_CHARS, GIT_COMMIT_PREFIX, DEFAULT_TEST_CMD,
)
from .tasks import load_tasks, find_test_doc
from .runner import (
    run_tests, extract_failure_count,
    detect_task_test_files, _looks_like_test_file,
)
from .claude import (
    run_claude, parse_reset_time, handle_session_limit,
)
from .prompts import (
    build_implement_prompt, build_fix_prompt, build_critic_prompt,
    build_write_tests_prompt, parse_critic_output, format_elapsed,
)
from .status import update_task_status, STATUS_REL_PATH, STATUS_WIDTH
from .git_ops import (
    git_commit_task, get_completed_task_ids, get_last_orchestrator_task_id,
    git_reset_hard, resume_check,
)
from .loops import ralph_loop, critic_loop, write_tests_phase
from .main import main
