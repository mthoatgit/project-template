# ADR 0002 — Availability is asserted by resolving the console script, and only at scaffold time

**Status:** accepted
**Date:** 2026-08-15
**Source-item:** [[035-orchestrator-own-repo-package]]
**Source-REQs:** REQ-0003

## Context

`REQ-0003` requires `/new-project` to determine whether the shared orchestrator installation is available and to report when it is not. It was the only requirement of item 035 to reach Stage 3 carrying `pending`, because three separate things were open: what the check inspects, where it runs, and what it means for this project to make an assertion about another project's installation at all.

Under the shared-installation model nothing inside a scaffolded project records that the loop must be installed. That is the intended shape — [ADR 0001](0001-tech-stack.md) commits to depending rather than carrying — but it produces a specific failure mode. A machine that has never installed the orchestrator produces projects that look complete and fail at the first invocation with a command-not-found or import error, a symptom that points nowhere near its cause. `/new-project` is the one moment where the machine's state and the user's attention coincide.

Three candidates were weighed in the item's Stage 3 Discussion:

- **Check that the clone directory exists** at a known path. Rejected outright. It passes on a machine where the clone was never installed — the likelier of the two failures — and so would report success on a setup that cannot run the loop.
- **Check the directory and the console script**, so the report can distinguish "not cloned" from "cloned but not installed". Rejected on the minimalism rule. The case it uniquely catches is already served by a single check whose failure message names both causes; the second probe buys a diagnosis the reader reaches from the message anyway.
- **Check that the console script resolves.** Chosen. It is the exact surface `consuming-the-orchestrator.md` tells users to invoke, and it proves the clone and the installation together in one step rather than proving one and assuming the other.

The stance underneath matters more than the mechanism. This repository is asserting another repository's install contract, and doing so with a blind spot that the orchestrator's own `ADR-0003` names among its negatives: the editable install is per Python environment, so a project with its own virtualenv needs the install repeated there, and nothing in that project records the requirement. A check running in `/new-project`'s shell will therefore pass while the project's own environment lacks the package. Left unwritten, the next person to meet that case fixes it by recording install state per project — which is vendoring in different clothing, and a reversal of the decision this item exists to implement.

## Decision

`/new-project` MUST determine orchestrator availability by resolving the `orchestrator` console script, and MUST NOT infer availability from the presence of a clone directory.

A failed resolution MUST be reported to the user naming both possible causes — no clone, or a clone that was never installed — and MUST NOT fail the scaffold. The project MUST still be created.

The check MUST run only at scaffold time. No scaffolded project MUST record, pin, or verify the orchestrator installation on its own behalf, and no per-project state describing the installation MUST be written.

The blind spot MUST be accepted as stated: the check proves availability in the environment it runs in, and a project using a separate Python environment MAY still lack the package despite a passing check. Closing that gap by giving projects their own installation state is a reversal of this decision and of the orchestrator's `ADR-0003`, not a refinement of either.

## Consequences

- **Positive:** The failure mode that the shared-installation model creates is caught at the only moment it can be caught cheaply, and reported in terms the user can act on. One probe covers both halves of "obtain it" — clone and install — because it tests the thing the user was told to run rather than a proxy for it. Nothing is added to the scaffolded project, so the check costs no per-project surface and cannot itself drift.
- **Negative:** The check is honest but not complete. A per-virtualenv project passes the check and fails at invocation, and this decision explicitly declines to fix that, which means a real failure mode stays open by choice. The check also asserts a contract this project does not own: if the orchestrator ever stops shipping a console script, the check breaks here while the cause lives in another repository, with nothing mechanical connecting the two.
- **Neutral / trade-off:** Reporting rather than installing keeps `/new-project` a scaffolding command rather than a machine-provisioning one. The cost is that a user on a fresh machine gets a message instead of a working setup, and must run two commands from the orchestrator's own documentation before the project they just created can be implemented.
