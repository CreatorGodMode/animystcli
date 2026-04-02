You are executing Phase 03 of the Animyst autonomous refactor.

Read `docs/ralph-tasks/03-history.md`, implement persistent history and resume behavior, verify, and stop after the scoped commit.

Rules:
- persist every user and assistant turn
- degrade safely if history files are malformed
- surface persisted summary metadata in the app

