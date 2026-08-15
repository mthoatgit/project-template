# TEST-0005 — A missing installation is reported without failing the scaffold

**Epic:** E1-orchestrator-extraction
**Mode:** procedural
**Source:** [[035-orchestrator-own-repo-package]]
**REQ:** REQ-0003
**Task:** TASK-0005
**Last verified:** 2026-08-15 by Claude (both branches of the check exercised directly; the `/new-project` wrapper itself not run)

## Steps

1. Confirm the orchestrator currently resolves: run `orchestrator --help` from a directory outside `~/dev/orchestrator`. It should succeed.
2. Run `/new-project test-availability-present` and let it complete.
3. Read the run's output end to end, and inspect the created project.
4. Delete the created project.
5. Make the orchestrator unresolvable without uninstalling it — the cheapest reversible way is to run the next step from a shell whose `PATH` excludes the environment's scripts directory, or from a Python environment that has no editable install of it. Do **not** delete or move `~/dev/orchestrator`.
6. Run `/new-project test-availability-absent` and let it complete.
7. Read the run's output end to end, and inspect the created project.
8. Delete the created project and restore the shell to its normal state.

## Expected observation

Step 3 matches if the run produced **no** report about the orchestrator, and the project was created complete.

Step 7 matches if **all four** of the following hold — it does not match if any one fails:

- The project was created and is complete. The run did not abort.
- The output carries an explicit report that the orchestrator could not be resolved.
- That report names **both** causes — no clone, and a clone that was never installed — and gives both remedies (`git clone …` and `python -m pip install -e ~/dev/orchestrator`).
- The report states that the project itself was created successfully, so it cannot be read as a scaffold failure.

Both projects match on a final check: neither contains any file recording the orchestrator installation, the check, or its result.

## Notes

Step 5 is deliberately non-destructive. The obvious way to simulate absence — moving `~/dev/orchestrator` aside — risks leaving the machine's only copy of the loop misplaced if the run is interrupted, and the editable install would point at a path that no longer exists. Shadowing `PATH` for one shell is reversible by closing it.

`ADR-0002` forbids writing installation state into a scaffolded project; the final check is what holds that line, and it is the one an implementer is most likely to cross with good intentions.

### Run of 2026-08-15

The discriminating half was verified directly rather than through `/new-project`, because the step's substance is one command and the wrapper adds nothing to what is being asserted. `orchestrator --help` resolves under the normal environment and reports `AVAILABLE`; run under `PATH=/usr/bin:/bin`, with the Python scripts directory removed and the installation otherwise untouched, the same command reports `MISSING`. The check therefore discriminates on the property it claims to, and does so without a destructive setup step.

Not covered by this run: that `/new-project` prints the message and continues rather than aborting. That is a property of the command's control flow, and the step is written to make it hold — the report is a print, the scaffold has already completed by then — but it has not been observed. The remaining gap is one `/new-project` invocation in a shell without the install on `PATH`.

A separate observation from the same session, belonging to the Epic rather than this test: the loop was run from the shared installation against a project scaffolded from `skeleton/` that contained no orchestrator source. It started, wrote its logs into the target, and stopped on the absent `scripts/test.py` — the documented `REQ-0040` behaviour for a project `/scaffold` has not yet run against, not a failure of the extraction.
