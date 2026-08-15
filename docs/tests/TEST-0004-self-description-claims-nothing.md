# TEST-0004 — The self-description claims no ownership of the loop

**Epic:** E1-orchestrator-extraction
**Mode:** structural
**Source:** [[035-orchestrator-own-repo-package]]
**REQ:** REQ-0004
**Task:** TASK-0004

## Assertion

`CLAUDE.md` and `README.md` MUST NOT describe this project as owning, testing, or specifying the orchestrator; MUST NOT reference `skeleton/orchestrator/`, `orchestrator-tests/`, or `pytest.ini` as things that exist; MUST name `~/dev/orchestrator` as the loop's home; and every path either document names in its layout description MUST exist.

## Verified by

```sh
cd ~/dev/project-template

# 1. No ownership claim, no reference to deleted paths.
! grep -nEi 'canonical orchestrator source|orchestrator-tests|pytest\.ini|skeleton/orchestrator|[0-9]+ tests covering' CLAUDE.md README.md || {
  echo "FAIL: a stale ownership claim or deleted path survives"; exit 1; }

# 2. Both name where the loop actually lives.
for f in CLAUDE.md README.md; do
  grep -q '~/dev/orchestrator' "$f" || { echo "FAIL: $f does not name the loop's home"; exit 1; }
done

# 3. Every repo-relative path named in either document exists. Placeholder
#    paths are excluded: the match stops at the '<' of a token like
#    docs/backlog/001-<seed-slug>.md, leaving a fragment ending in '-'.
grep -ohE '(^|[ `(])(skeleton|docs|scripts)/[A-Za-z0-9_./-]*' CLAUDE.md README.md \
  | sed -E 's/^[ `(]//' | sed 's#/$##' | grep -vE '\-$' | sort -u \
  | while read -r p; do
      test -e "$p" || { echo "FAIL: documented path does not exist: $p"; exit 1; }
    done

echo "PASS"
```

## Notes

Check 3 is the one that earns this test's keep. Checks 1 and 2 assert that specific known-stale strings are gone and specific new ones are present, which a careful rewrite would satisfy by construction. Check 3 catches the failure that actually recurs: a tree diagram in `README.md` describing a layout that drifted. Both documents carry such diagrams, and both currently name paths this Epic deletes.

The `[0-9]+ tests covering` pattern targets `CLAUDE.md`'s current Verification line, which promises 164 orchestrator tests. It is written as a pattern rather than the literal number so that reinstating the claim with an updated count still fails.
