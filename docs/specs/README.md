# Requirements

## Goal

`project-template` supplies the structure every new project on this machine starts with — the folder shape, the document templates for each workflow stage, and the shared Claude Code and CI configuration — and is itself maintained through the workflow it hands out. It executes nothing. What it must guarantee is that a project created from it is immediately workable, that improvements made here reach the next project without anyone copying files, and that a project can say how its own tasks get implemented even when the thing implementing them lives elsewhere.

## Domain

Developer tooling — project scaffolding and workflow supply.

## Out of Scope (for now)

- The orchestrator loop itself: its code, its test suite, and its specification. It lives in `~/dev/orchestrator` and is consumed from one shared installation.
- Per-project pinning of the orchestrator version — decided against in that project's `ADR-0003`.
- The workflow skills and slash commands, which live in `~/.claude` and are distributed from `dotfiles-claude`.
- Executing, building, or testing anything. This project has no runtime code and no test suite of its own.
- Pushing later template changes into projects that were already scaffolded. Once a project exists it owns its files; there is no update channel.

## Epics

| Epic | Name | Folder | Covers |
|---|---|---|---|
| E1 | Orchestrator extraction | [epics/E1-orchestrator-extraction/](epics/E1-orchestrator-extraction/) | REQ-0001..REQ-0007 — remove the loop from the scaffold, replace it with a reference to the shared installation, and de-vendor the project that already holds a copy |
