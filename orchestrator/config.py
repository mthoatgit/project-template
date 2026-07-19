"""Configuration constants for the orchestrator.

These are the load-bearing knobs. Change here to change behaviour.
Documented in `docs/orchestrator-requirements.md`.
"""

# Maximum fix attempts per task in the Ralph Loop.
# 5 is a good ceiling: simple tasks fix in 1–2 rounds, complex ones
# rarely benefit from more. Smart early-exit handles stuck cases
# before this ceiling is reached.
MAX_ITERATIONS = 5

# How many consecutive iterations with the same failure count before
# we consider Claude conceptually stuck and abort.
# 2 means: if round N and round N+1 both show the same number of
# failures, the fix attempts aren't helping.
STUCK_STREAK_THRESHOLD = 2

# Maximum Critic review cycles per task.
# After tests pass, the Critic evaluates the solution approach.
# 3 is appropriate: a good solution usually gets approved in 1–2 rounds;
# more rarely helps when the approach is fundamentally wrong.
MAX_CRITIC_ITERATIONS = 3

# Maximum characters of test output fed back to Claude per iteration.
# Keeps prompts focused; the tail is kept (most recent failures are most useful).
MAX_ERROR_CHARS = 6000

# Prefix used in git commit messages to identify orchestrator commits.
GIT_COMMIT_PREFIX = "[orchestrator]"

# Default --test-cmd. Every project generated from this template is expected
# to carry a scripts/test.py runner (written by /scaffold from the tech
# stack in system-design.md) that dispatches to the right test tools. Keeps
# the orchestrator itself framework-agnostic.
DEFAULT_TEST_CMD = "python scripts/test.py"

# ── Option-H DoD gates (backlog item 028) ─────────────────────

# Maximum docs_write ↔ final_approval iterations before the loop force-
# routes to a design fix. 2 means: after one Phase-3/Phase-4 round-trip
# that didn't approve, the next docs-only reject is treated as evidence
# that docs alone are not the problem — Guardrail 3 in item 028.
MAX_DOCS_CYCLES = 2

# Files that Phase-3 (docs_write) is required to bring into sync with the
# code change and Phase-4 (final_approval) checks for coverage. Paths are
# relative to the project root. Starter list; can be lifted into a per-
# project override later (see open questions in backlog item 028).
MANDATORY_DOC_FILES = ["README.md", "CLAUDE.md"]
