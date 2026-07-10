# P3 · Dashboard doesn't display Type column

- **Symptom.** Merged index has `Type: task | bug`, but the dashboard frontend Task table renders only ID / Epic / Title / Status. Bugs render identically to tasks in the UI.
- **Impact.** Cosmetic; nothing depends on it. Anyone using the dashboard can't visually tell tasks from bugs.
- **Proposed shape.** Thread `type` through the backend `Task` dataclass + `/api/tasks` response, add a column to the `TaskTable` widget. Small feature, one atomic task.
- **Source.** 2026-07-09 session — noted while smoke-testing the app.
