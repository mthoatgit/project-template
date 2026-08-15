# Test Strategy

## Work-item anchoring

**The REQ is the anchor.** REQ = the *WHAT* (behavior promised, structural claim). Everything else revolves around it — Task implements one or more REQs (*HOW*); Test verifies one or more REQs (*proof that the WHAT holds*).

```
                    REQ (WHAT)
                    stable ID
                    ↑        ↑
        implements /          \ verifies
                  /            \
              TASK              TEST
              (HOW)         (proof WHAT holds)
              ↓                  ↑
              └──────────────────┘
              **Task:** header — one primary task (the Ralph-Loop anchor)
              **Also-covers:** header — additional tasks the test observes
              (informational; the orchestrator ignores it)
```

**Metadata in each file (the primary SoT).**

- `docs/tasks/TASK-<NNNN>-*.md` carries a `## Requirements` section listing REQ IDs it implements.
- `docs/tests/TEST-<NNNN>-*.md` carries these header fields:
  - `**REQ:**` — the REQs it verifies (the anchor). One or more, comma-separated.
  - `**Task:**` — **exactly ONE** task ID: the *primary* task whose Ralph Loop must green this test.
  - `**Also-covers:**` — OPTIONAL. Additional task IDs the test exercises as a side effect. Informational only; the orchestrator ignores this field. See `workflow-tests` "Work-item anchoring" for the single-`**Task:**` rationale.

**Relationship cardinality.**

- REQ ↔ Task: many-to-many. One task MAY implement multiple REQs; one REQ MAY be served by multiple tasks.
- REQ ↔ Test: many-to-many. One REQ MAY have multiple tests (e.g. structural + procedural for the same REQ — see three modes below); one test MAY cover multiple REQs.
- Task ↔ Test (primary via `**Task:**`): each test has ONE primary task; each task MAY have multiple tests.
- Task ↔ Test (informational via `**Also-covers:**`): many-to-many, no orchestrator contract.

**Overview files are human aggregations, not SoT.** `docs/tasks/index.md` and `docs/tests/index.md` mirror the metadata that lives in the file headers. They exist for human reading — Coverage-Matrix, status-at-a-glance, filtering. Machines (orchestrator) MUST read from the file headers directly, not from the aggregations (which can drift).

**Machine discovery — how the orchestrator finds tests for a given task.**

```sh
grep -l '^\*\*Task:\*\* .*<task-id>' docs/tests/TEST-*.md
```

Cheap (~ms per hundred files), simple (single-line pattern anchored on `^\*\*Task:\*\*`), reliable (fixed template header format). No table parsing, no dependency. Returns matching file paths directly.

## Verification modes

Every REQ maps to at least one verification mode at Stage 5 (Tests) of the featurework lifecycle. The mode is chosen per REQ; a single Epic may carry REQs of different modes.

| Mode | What it verifies | How it runs | Typical scope |
|---|---|---|---|
| **Behavioral** | Observable runtime behavior against expected input/output | Automated test framework (pytest, flutter test, ...) | Feature code, bug fixes, any REQ with input→output semantics |
| **Structural** | Mechanically verifiable claims about codebase / docs / config structure | Shell scripts, linters, grep / find / diff assertions | Docs work, config changes, schema migrations, rename cascades |
| **Procedural** | Ordered human checklist with expected observations | Human runs steps, ticks off | Editorial quality, discoverability, UX impressions, anything not mechanically checkable but load-bearing |

**Mode-selection rule.** If a REQ describes observable behavior, choose Behavioral. If it describes structural constraints on artefacts (files exist, headers present, patterns not matched), choose Structural. If it demands a human quality judgement, choose Procedural. When a REQ genuinely admits multiple modes (e.g. a documentation REQ that needs both a grep-able presence check AND a human discoverability judgement), file **multiple tests, one per mode** — one test = one atomic verification intent.

The `workflow-lifecycle-featurework` rule "Stage 5 cannot be null" is preserved. "Not null" means "produces artefacts in one of the three modes" — not "produces pytest scenarios specifically".

## Behavioral tests

Standard test-pyramid discipline for runtime code.

| Layer | Purpose | Tools |
|---|---|---|
| **Unit** | Pure logic in service classes / pure functions, no framework context | <test framework, e.g. pytest / JUnit / flutter test> |
| **Slice** | Persistence or web layer in isolation | <slice test utilities per framework> |
| **Integration** | Module wiring with real dependencies | <containers, full-context bootstrap, real HTTP client> |
| **E2E** | Full system over HTTP / public API | <real backend + real client> |

**"Done" per layer** (fill in per project):
- A **service / use case** is done when <criterion>.
- A **repository / persistence** is done when <criterion>.
- A **controller / API endpoint** is done when <criterion>.
- The **system** is done when <the E2E happy-path scenario passes>.

**Entry-point anchoring** (from `workflow-tests`): for every user-observable outcome, at least one behavioral scenario per Epic MUST exercise the code from the first user contact — root widget rendered via `main()` for UI, real HTTP call with an external `Origin` header for a web API, `main()` for a CLI. Widget/unit-in-isolation scenarios are welcome IN ADDITION, never INSTEAD.

## Structural tests

Verifiable structural claims — the "did the migration / change actually complete as declared?" check.

Each structural test file carries:
- `**Assertion:**` — the structural claim in RFC 2119 language.
- `**Verified by:**` — the exact command / script / regex that verifies the assertion. MUST be runnable as-is (or trivially adapted for the runner). Prefer POSIX shell + `git`, `find`, `grep`, `diff`, `test`; escalate to a project script only when a one-liner would obscure intent.
- Expected result: exit code `0` = pass; non-zero = fail.

Structural tests execute either in CI (shell step) or in the orchestrator's per-iteration verification phase alongside behavioral tests.

## Procedural tests

Playbook format for human-verified checks.

Each procedural test file carries:
- `**Steps:**` — ordered, concrete steps the human takes.
- `**Expected observation:**` — what the human should see. Formulated as a **binary judgement** (matches / does not match), not a fuzzy impression.
- `**Last verified:**` — date + who, updated each time the playbook is run manually.

Procedural tests never execute in CI. Their pass/fail is recorded in the test file's `**Last verified:**` field after each manual check.

## Test data & fixtures

- No shared mutable state between tests.
- Behavioral fixtures live alongside the test file that uses them; cross-cutting fixtures under `docs/tests/cross-cutting/`.
- Structural tests: fixtures are the repository state itself (or a `git show` of a specific commit).
- Procedural tests: fixtures are usually the running application; the playbook says how to bring it up.

## CI Integration

This project has no test runner and no CI test job, which follows from [ADR 0003](../adr/0003-medium-and-dependencies.md) — no product, no test suite, no build step. That is not an omission to be filled in later; a suite asserting the shape of a directory of Markdown templates would verify their form rather than their usefulness, and usefulness is the property that matters here.

- **Behavioral** — not used. Nothing in this repository executes, so there is no input-to-output semantics to assert.
- **Structural** — each test's `## Verified by` block is runnable as-is and is executed by hand when the test is checked. There is no aggregate runner and no merge gate; the commands are the specification of what "correct" means, and running them is a step in the end-of-Epic self-review.
- **Procedural** — never CI, here or anywhere. Verified by a human, with the result recorded in each file's `**Last verified:**` field.

A structural test in this project therefore fails loudly only when someone runs it. That is the cost side of ADR 0003 and is named in its Consequences: nothing here is mechanically verified, and a broken template or stale instruction is discovered by the next person to scaffold.
