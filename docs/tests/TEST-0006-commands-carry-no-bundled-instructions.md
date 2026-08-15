# TEST-0006 — The scaffolding commands carry no bundled-orchestrator instructions

**Epic:** E1-orchestrator-extraction
**Mode:** structural
**Source:** [[035-orchestrator-own-repo-package]]
**REQ:** REQ-0006
**Task:** TASK-0006

## Assertion

Neither `/new-project` nor `/init-project` MUST instruct on removing orchestrator files or `pytest.ini` from a project, `/init-project`'s remaining steps MUST be contiguously numbered, and `/scaffold` MUST be unchanged by this Epic.

## Verified by

```sh
cd ~/.claude/commands

# 1. No instruction to remove orchestrator artefacts from a project.
! grep -nE 'rm -rf orchestrator|rm -f +pytest\.ini|orchestrator tests to remove|pytest\.ini to strip' \
    new-project.md init-project.md || {
  echo "FAIL: a bundled-orchestrator instruction survives"; exit 1; }

# 2. /init-project's steps are contiguous from 1 with no gap left by the removal.
grep -oE '^[0-9]+\. ' init-project.md | tr -d '. ' | awk '
  {if ($1 != NR) {printf "FAIL: step numbering breaks at %s (expected %d)\n", $1, NR; exit 1}}
  END {if (NR == 0) {print "FAIL: no numbered steps found"; exit 1}}' || exit 1

# 3. /scaffold is untouched by this Epic. e33de6e is dotfiles-claude's HEAD
#    at the moment Stage 4 closed — the last state before implementation.
git -C ~/.claude diff --quiet e33de6e -- commands/scaffold.md || {
  echo "FAIL: scaffold.md changed; this Epic must not touch it"; exit 1; }

echo "PASS"
```

## Notes

Check 2 exists because removing step 0 forces a renumber, and a renumber is exactly the kind of edit that silently leaves a gap or a duplicate. `TASK-0006` also asks whether any later text refers to a step number that moved; no mechanical check covers that, and it stays a reading task for the implementer.

Check 3 pins `scaffold.md` against `dotfiles-claude`'s own HEAD at the moment Stage 4 closed — the last state before this Epic's implementation begins. It asserts a *non*-change, which is unusual for a test but is the point: `/scaffold` invokes `python -m orchestrator` and looks like it needs fixing. It does not — that form resolves from the installed package — and this check is what stops a well-meaning edit.

Both files live in `dotfiles-claude`, so these commands run against a different repository than the one this test file sits in.
