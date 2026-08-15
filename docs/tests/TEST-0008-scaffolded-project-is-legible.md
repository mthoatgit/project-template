# TEST-0008 — A scaffolded project explains its own execution to a cold reader

**Epic:** E1-orchestrator-extraction
**Mode:** procedural
**Source:** [[035-orchestrator-own-repo-package]]
**REQ:** REQ-0002
**Task:** TASK-0002
**Also-covers:** TASK-0001
**Last verified:** never

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
