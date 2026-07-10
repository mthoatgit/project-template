# P2 · Logging is prose-mixed, hard to reconstruct retrospectively

- **Symptom.** Orchestrator writes two log files per run — a full log and a filtered progress log — but both are raw prose mixing prompts, Claude subprocess output (long Flutter/pytest test dumps), status markers (`[Ralph Loop]`, `[Fix]`, `[Critic]`, `[OK]`, `[FAIL]`), and errors in one chronological stream. No structured filtering, no per-item organization, no decision-point index, no explicit exit-reason surface. When an item ends `action needed`, the *why* is buried in prose.
- **Impact.** The orchestrator runs asynchronously to the user's attention — background, minutes to hours per run. When it's done, the user has to collaborate with Claude retrospectively to find what went wrong. Today that means scrolling thousands of lines of test output for a magic string that may or may not exist. The primary block on effective post-hoc diagnosis.
- **Proposed shape.** Options to put on the table (probably some combination):
  - **Structured JSONL sidecar** — each decision-worthy event (prompt sent, tests started, iteration N result with fail count, critic verdict, commit produced, exit) as a JSON line; keep the prose log for reading, use JSONL for filtering.
  - **Per-item log tree** — `logs/orchestrator-<timestamp>/<ID>/{prompt.md, tests-1.log, critic.md, decision.txt, ...}`. Filesystem *is* the index; you `cd` to the item that broke.
  - **End-of-run summary** — `-summary.md` per item: outcome, exit reason if aborted, iteration count, deciding failure output, commit SHA. Points into detail logs.
  - **Timestamps on every internal marker** — enables wall-clock reconstruction and correlates with external signals.
  - **Collapse repeated test output** — keep first + last iteration's test dump verbatim, elide the middle with a count marker so 500 identical lines become one.
- **Source.** 2026-07-09 session — user: "der orchestrator läuft getrennt von meiner wahrnehmung und daher brauche ich retrospektiv die möglichkeit zusammen mit dir besser fehler zu finden."
