# ADR 0001 — Files only, and a standing dependency on two sibling repositories

**Status:** superseded by [ADR 0003](0003-medium-and-dependencies.md)
**Date:** 2026-08-15
**Source-item:** [[035-orchestrator-own-repo-package]]
**Source-REQs:** none — founding ADR, produced under the founding-ADR rule rather than by a requirement. `REQ-0004` removes the last of the code this decision records the absence of.

## Context

`docs/adr/` was empty, so the founding-ADR rule in `workflow-lifecycle-featurework` applies: the first Stage 3 to run must produce ADR-0001 and may not null-decide. It falls to item 035 rather than to an item 001, because items 001..034 were retro-documented without ever running the lifecycle.

The timing is fortunate rather than awkward. Before this item, a tech-stack ADR here would have described Python 3.11+, a stdlib-only runtime, and a 164-test pytest suite — all of which belong to the orchestrator and are leaving under `REQ-0004`. Afterwards roughly all of this repository's code is gone and what remains is Markdown, a directory shape, and configuration files copied verbatim into new projects. There is no language, no runtime, no build step, and nothing to execute. A tech-stack ADR for a project in that position is unusual but not empty: the absence is the commitment, and stating it prevents the slow accretion of tooling that has no user.

The second half is the harder one. `docs/concept.md` records under Constraints that three repositories must stay in agreement and none is versioned with the others — this one, `~/dev/orchestrator` for the execution engine, and `dotfiles-claude` for the skills and commands. That is currently a line in a prose document, which makes it read as an observation. It is not an observation, it is a position, and it was arrived at deliberately: the orchestrator's `ADR-0003` chose one shared installation over per-project pinning, and this project's role was narrowed in the same decision to ensuring availability. Recording it as architecture is what makes a future proposal to vendor, pin, or sub-module either of those repositories legible as a reversal rather than an improvement.

The alternative shape considered was splitting this into two ADRs — one for the stack, one for the dependency stance. It was rejected as artificial. For a project with no code, what it is made of and what it leans on are the same subject, and a stack ADR that omitted the two repositories would describe a project that cannot actually do anything.

## Decision

`project-template` MUST hold no runtime code, no test suite, and no build step. Its medium is Markdown documents, directory structure, and configuration files consumed verbatim by the projects it scaffolds. Anything that must execute MUST live in another repository and be depended on, not carried.

This project MUST depend on `~/dev/orchestrator` for task execution and on `dotfiles-claude` for the workflow skills and commands, and MUST NOT version, vendor, pin, or sub-module either of them. Consumption of the orchestrator MUST follow that project's `ADR-0003` — one shared installation, always latest — and this project's responsibility MUST remain limited to ensuring availability and stating the reference.

Correctness of what this project supplies MUST be established by inspection of the scaffolded result, not by a test suite executed here.

## Consequences

- **Positive:** There is nothing to install, build, or run in order to use what this project supplies, and no dependency that can rot. A reader can understand the whole project by reading it. The removal of the orchestrator stops being a subtraction that leaves a gap and becomes the shape of the thing: improvements to execution reach every project at once through the shared installation, which is precisely what the copy-per-project arrangement could not do.
- **Negative:** Nothing here is mechanically verified. A broken template, a stale instruction, or a scaffold that produces an unworkable project fails silently and is discovered by the next person to scaffold — the `question` lifecycle surviving in `README.md` for several commits after its removal is a small example of exactly this. The three-repository split also means no single commit, tag, or checkout describes a working whole; reconstructing the state of this system at a past date requires three histories and the knowledge that they exist.
- **Neutral / trade-off:** Choosing to depend rather than carry is the same trade the orchestrator's `ADR-0003` made and is accepted here on the same terms — a breaking change in either sibling repository is felt immediately and everywhere, and the compensation is that a fix is too. Verification by inspection is accepted rather than tolerated: a test suite for a directory of Markdown templates would assert their shape, not their usefulness, and the useful properties are the ones only a reader can check.
