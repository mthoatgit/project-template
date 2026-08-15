# TEST-0008 — A scaffolded project explains its own execution to a cold reader

**Epic:** E1-orchestrator-extraction
**Mode:** procedural
**Source:** [[035-orchestrator-own-repo-package]]
**REQ:** REQ-0002
**Task:** TASK-0002
**Also-covers:** TASK-0001
**Last verified:** 2026-08-15 by a context-free subagent (steps 1-4; the reader was an agent with no knowledge of this work rather than a fresh interactive session)

## Steps

1. Run `/new-project test-legibility` and let it complete.
2. Open a fresh Claude Code session in the created project. Do not carry context in from elsewhere.
3. Ask it two questions and nothing more: *"How do tasks get implemented in this project?"* and *"Where does the code that implements them live?"*
4. Note whether the answers came from `CLAUDE.md` alone or required opening other files.
5. Delete the created project.

## Expected observation

Matches if the session answers both questions correctly from `CLAUDE.md` alone — naming the `orchestrator --tasks docs/tasks/ --project-dir .` invocation, and stating that the code is installed rather than part of the repository, with `~/dev/orchestrator` as its source.

Does not match if the session says the project has no implementation loop, cannot say where the engine lives, guesses at a path, or has to search the filesystem to answer.

## Notes

This is the test `TEST-0002` cannot be. That one greps for strings and will pass on any file containing them in any arrangement; this one asks whether a reader actually learns from them, which is the promise `REQ-0002` makes and the whole reason the requirement exists. De-vendoring removes evidence rather than capability — the project runs fine either way — so a legibility failure is invisible to every mechanical check in this Epic.

Step 2's insistence on a fresh session is the load-bearing part of the procedure. A session that has already discussed this Epic knows the answer and will produce it regardless of what the file says, which would make the test pass while proving nothing.

A human reader may substitute for the session in step 3. The judgement is the same: two questions, answered from one file, without prior knowledge of this machine's layout.

### Run of 2026-08-15 — matched

A project was scaffolded from `skeleton/` into a scratch directory, filled per `/init-project`, and `init-verify.py` run against it. The cold reader was a subagent launched with no context of this work and no access to the conversation that produced the file — the requirement in step 2 is a reader with no prior knowledge, and an agent that has never seen this repository satisfies that more strictly than a human on the same machine would.

It was given the project path, told to read `CLAUDE.md` and nothing else, and asked the two questions plus three follow-ups about what it could not answer.

Both answers were correct and unaided. It gave the invocation, and stated that the code is not in the repository, lives at `~/dev/orchestrator`, is installed once per machine, and that a command-not-found means a missing installation rather than a broken project. Asked directly whether it had to guess, it said no, and volunteered that the section was *"unusually explicit and unambiguous about both the mechanism and the code's location"*.

Its criticisms all landed on the surrounding template placeholders — build, test, run and lint still unfilled, `Code Layout` and `Gotchas` still `<...>` — which are artefacts of the deliberately minimal fill used for this run, not of anything this Epic changed.

One piece of feedback is worth keeping and is out of scope here: the reader noted that the `MUST NOT implement tasks manually` rule is stated but never scoped, so nothing tells it what to do when the orchestrator genuinely cannot run. Epic 1 was itself that case. Recorded rather than acted on.

The reader also said that, left unrestricted, it would have opened `~/dev/orchestrator/docs/consuming-the-orchestrator.md` next. That the file gave it a name to go looking for is the property this test exists to check.
