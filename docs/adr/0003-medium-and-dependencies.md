# ADR 0003 — No product, no build, no runner — and a standing dependency on two sibling repositories

**Status:** accepted
**Date:** 2026-08-15
**Source-item:** [[035-orchestrator-own-repo-package]]
**Source-REQs:** none — supersedes the founding ADR-0001, which was likewise not REQ-driven. `REQ-0004` removes the code whose absence both ADRs describe.

## Context

This supersedes [ADR 0001](0001-tech-stack.md), which committed the project to holding *no runtime code* and stated that anything which must execute belongs in another repository and is depended on rather than carried. That was false when it was written, and the failure is worth recording accurately rather than tidying away.

`scripts/init-verify.py` — 226 lines of Python that execute — had been in the repository since commit `1186404`, two weeks before ADR-0001 was accepted. ADR-0001 was written from a picture of what the project would look like once the orchestrator left, without checking what was already on disk. It was not made wrong by later drift; it was wrong on the day.

The circumstances that produced it are part of the diagnosis. ADR-0001 exists because the founding-ADR rule in `workflow-lifecycle-featurework` requires the first Stage 3 to produce a tech-stack ADR and forbids null-deciding while `docs/adr/` is empty. Item 035 had no technology to choose, so the obligation was met by describing an absence. An ADR that records a decision has decision pressure behind it — someone weighed alternatives and had to defend one. An ADR that records an absence has none, and is correspondingly easy to write without verifying.

The absolute also did not buy what it claimed. ADR-0001 argued that "there is nothing to install, build, or run in order to use what this project supplies". That was already untrue in two ways: `init-verify.py` needs Python, and a project scaffolded from here needs `pip` in its environment before the orchestrator can implement anything.

Two ways forward were weighed. Moving `init-verify.py` into `dotfiles-claude`, beside the `/init-project` command that is its only caller, would make ADR-0001 literally true without amending it. It was rejected on where the knowledge lives: the script encodes `project-template`'s scaffold shape — the `<test-cmd>` placeholder, item 001's frontmatter fields, the template banners — and belongs next to the thing it knows. The cross-repository invocation is one absolute path in a command file, which is a small cost against splitting that knowledge in two.

What survives ADR-0001 untouched is its second half. The dependency stance is correct, is load-bearing, and is restated here verbatim in substance: it is what makes a future proposal to vendor the orchestrator again read as a reversal rather than a convenience.

## Decision

`project-template` MUST NOT hold runtime code, a build step, or a test suite of its own. Its medium MUST remain Markdown documents, directory structure, and configuration files consumed verbatim by the projects it scaffolds.

Executable tooling MAY exist here only as a scaffold-time helper: a script invoked from outside this repository, operating on a target project, with no role in what this repository supplies at rest. `scripts/init-verify.py` is the one such helper today. Anything that must execute as part of a *product* MUST live in another repository and be depended on, not carried.

This project MUST depend on `~/dev/orchestrator` for task execution and on `dotfiles-claude` for the workflow skills and commands, and MUST NOT version, vendor, pin, or sub-module either of them. Consumption of the orchestrator MUST follow that project's `ADR-0003` — one shared installation, always latest — and this project's responsibility MUST remain limited to ensuring availability and stating the reference.

Correctness of what this project supplies MUST be established by inspection of the scaffolded result, not by a test suite executed here.

## Consequences

- **Positive:** The constraint is now enforceable, which the absolute was not. "Is this a scaffold-time helper invoked from outside, or a product growing here?" is a question with an answer; "does anything execute?" had an answer the repository already contradicted. Everything the absolute was actually aimed at — this project acquiring a runner, a build, or a product — is still rejected. The dependency stance carries over unweakened, so E1's requirements keep the architectural backing they were written against.
- **Negative:** A permission is easier to widen than a prohibition. "Scaffold-time helper" has no mechanical test, and a second script, then a third, each individually defensible, is how a directory of Markdown acquires a toolchain. Nothing here prevents that except a reader noticing. The failure that produced this ADR also stays visible in the log: `docs/adr/` now carries a superseded founding ADR from the same day as its replacement, which is untidy and is the honest record.
- **Neutral / trade-off:** Keeping `init-verify.py` here accepts a cross-repository call by absolute path from `/init-project`, in exchange for keeping the script beside the scaffold shape it encodes. Verification by inspection is unchanged from ADR-0001 and accepted on the same terms — a suite asserting the form of Markdown templates would not test the property that matters.
