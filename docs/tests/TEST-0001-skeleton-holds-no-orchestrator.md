# TEST-0001 — The scaffold holds no orchestrator

**Epic:** E1-orchestrator-extraction
**Mode:** structural
**Source:** [[035-orchestrator-own-repo-package]]
**REQ:** REQ-0001
**Task:** TASK-0001

## Assertion

`skeleton/` MUST contain no orchestrator source, no `subprocess_settings.json`, and no file whose text refers to a bundled orchestrator directory.

## Verified by

```sh
cd ~/dev/project-template

# 1. No orchestrator directory or module anywhere under skeleton/
test -z "$(find skeleton -iname 'orchestrator*' -o -name 'subprocess_settings.json')" || {
  echo "FAIL: orchestrator artefacts remain under skeleton/"; exit 1; }

# 2. No text under skeleton/ describes a bundled loop. The word may appear —
#    CLAUDE.md must name the engine (TEST-0002) — but never as something the
#    project contains. These are the phrasings that would mean 'bundled'.
! grep -rniE 'bundled at|\./orchestrator/|orchestrator/ +\(the whole package\)|python -m orchestrator' skeleton/ || {
  echo "FAIL: skeleton/ text still describes a bundled orchestrator"; exit 1; }

echo "PASS"
```

## Notes

The second check is deliberately about phrasing rather than the bare word. `skeleton/CLAUDE.md` must go on naming the orchestrator — that is what `REQ-0002` requires — so a blanket `grep -c orchestrator` would fail the two requirements against each other. `python -m orchestrator` is included in the reject list not because it stops working (it resolves from the installed package) but because `TASK-0002` replaces it with the console-script form, and its reappearance would mean that change was undone.

`.gitignore` is covered by the second check: its current Python-section comment contains `./orchestrator/`.
