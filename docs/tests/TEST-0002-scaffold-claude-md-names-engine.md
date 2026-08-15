# TEST-0002 — The scaffold's CLAUDE.md names the engine and its home

**Epic:** E1-orchestrator-extraction
**Mode:** structural
**Source:** [[035-orchestrator-own-repo-package]]
**REQ:** REQ-0002
**Task:** TASK-0002

## Assertion

`skeleton/CLAUDE.md`'s `## Implementation` section MUST give the console-script invocation, MUST state that the orchestrator is installed rather than part of the project, MUST name `~/dev/orchestrator` as its source, and MUST preserve the `<test-cmd>` placeholder that `/init-project` fills.

## Verified by

```sh
cd ~/dev/project-template
impl=$(sed -n '/^## Implementation/,$p' skeleton/CLAUDE.md)

echo "$impl" | grep -q 'orchestrator --tasks docs/tasks/' || {
  echo "FAIL: console-script invocation missing"; exit 1; }
echo "$impl" | grep -qi 'installed' || {
  echo "FAIL: does not state the engine is installed"; exit 1; }
echo "$impl" | grep -q '~/dev/orchestrator' || {
  echo "FAIL: does not name where the source lives"; exit 1; }
echo "$impl" | grep -q '<test-cmd>' || {
  echo "FAIL: /init-project's fill placeholder was lost"; exit 1; }
echo "$impl" | grep -q 'python -m orchestrator' && {
  echo "FAIL: still gives the module-invocation form"; exit 1; }

echo "PASS"
```

## Notes

The `<test-cmd>` check is a regression guard, not a requirement of `REQ-0002`. `/init-project` fills that placeholder, and a rewrite of this section that silently resolved it would break scaffolding in a way nothing else in this Epic would catch.

This test proves the strings are present. It cannot prove a reader learns anything from them, which is the actual promise `REQ-0002` makes — see `TEST-0008`.
