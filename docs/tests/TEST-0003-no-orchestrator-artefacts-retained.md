# TEST-0003 — This repository retains no orchestrator artefacts

**Epic:** E1-orchestrator-extraction
**Mode:** structural
**Source:** [[035-orchestrator-own-repo-package]]
**REQ:** REQ-0004
**Task:** TASK-0003

## Assertion

The repository MUST contain no test module, no `pytest.ini`, and no `docs/orchestrator-requirements.md`; the verbatim copy of that document MUST exist in the orchestrator repository and MUST match what was deleted; and no `.gitignore` MUST justify its rules by reference to a bundled orchestrator.

## Verified by

```sh
cd ~/dev/project-template

for path in orchestrator-tests pytest.ini docs/orchestrator-requirements.md orchestrator; do
  test ! -e "$path" || { echo "FAIL: $path still exists"; exit 1; }
done

# The legacy requirements document must survive where it was moved to.
ref=~/dev/orchestrator/docs/backlog/reference/orchestrator-requirements-legacy.md
test -f "$ref" || { echo "FAIL: reference copy missing from the orchestrator repo"; exit 1; }
git -C ~/dev/project-template show 'a5b44d1:docs/orchestrator-requirements.md' \
  | diff -q - "$ref" >/dev/null || {
  echo "FAIL: reference copy differs from the file that was deleted"; exit 1; }

! grep -qiE 'orchestrator' .gitignore skeleton/.gitignore || {
  echo "FAIL: a .gitignore still justifies its rules by the orchestrator"; exit 1; }

echo "PASS"
```

## Notes

The `orchestrator` path is included in the deletion loop because an untracked `__pycache__` tree by that name existed at the root until 2026-08-15. It is gitignored, so a check of tracked files alone would have missed it and left the question "does this repository contain an orchestrator module?" ambiguous.

The diff is taken against commit `a5b44d1` — the last commit in which `docs/orchestrator-requirements.md` still existed here. Pinning the SHA rather than diffing against the working tree is what makes this check meaningful after the deletion lands.

`skeleton/.gitignore` is asserted here as well as in `TEST-0001`, from the opposite direction: that test rejects the phrasing, this one rejects the word anywhere in either ignore file. A `.gitignore` has no reason to mention the loop at all.
