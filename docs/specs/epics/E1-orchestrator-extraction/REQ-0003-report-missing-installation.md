# REQ-0003 — Scaffolding reports a missing shared installation

**Epic:** E1-orchestrator-extraction
**Status:** active
**Source:** [[035-orchestrator-own-repo-package]]
**Architecture-impact:** pending (see Stage 3)

`/new-project` MUST determine whether the shared orchestrator installation is available on the machine, and MUST report to the user when it is not, naming what is missing and how to obtain it.

A missing installation MUST NOT fail the scaffold. A project is still worth creating on a machine where the loop has not been installed yet, and the requirement is that the user learns of the gap at the moment it matters — not that the gap blocks unrelated work.

## Acceptance

Running `/new-project` on a machine where the orchestrator does not resolve produces a complete project *and* an explicit report of what is missing and how to install it. Running it on a machine where the orchestrator does resolve produces the project and no such report.

## Rationale

Availability and reference are two unequal halves of the same problem, and this is the smaller one. Availability is a once-per-machine fact — the clone exists at a known location and `pip install -e` has run against the environment projects use — and it is not a per-project concern at all. Nothing in this requirement makes it one: the check reports, it does not install, and it does not record anything in the scaffolded project.

The failure mode it addresses is specific. Under the shared-installation model nothing inside a project records that the loop must be installed, so a machine that has never installed it produces projects that look complete and fail at the first `orchestrator` invocation with an import or command-not-found error — a symptom that points nowhere near its cause. `/new-project` is the one moment where the machine's state and the user's attention coincide.

## Related

- [[REQ-0006]] — the other change this Epic makes to the same commands, in the opposite direction: removing text rather than adding a check.
