# P2 · Dirty working tree after abort

- **Symptom.** When Ralph or Critic hit an exit criterion, whatever Claude last wrote stays in the working tree. The next run has to reconcile the leftover changes before it can proceed cleanly.
- **Impact.** Manual clean-up cost on every aborted run. Also confuses `resume_check` if the leftover changes overlap with the next item's scope.
- **Proposed shape.** On abort, either `git stash push -u -m "orchestrator-abort <ID>"` to preserve Claude's work in a labelled stash, or `git checkout HEAD -- <changed>` for a clean rollback. Keep `docs/tasks/index.md`'s `action needed` state — that IS the intended abort signal and must persist.
- **Source.** Earlier session, documented in `[[project_orchestrator_open_issues]]`.
