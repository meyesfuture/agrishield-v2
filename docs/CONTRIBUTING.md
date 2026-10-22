# Contribution & Working Rules

1. Read `AGENTS.md`, `PRD.md`, `ARCHITECTURE.md` and `PROJECT_STATE.md` before making broad changes.
2. Work in small phases and keep each phase testable.
3. Do not edit source-drop data or uploaded source reports; generate new processed artifacts instead.
4. Every transformation needs a script, test and provenance record.
5. Use meaningful names and type definitions. Avoid a giant monolithic component or service.
6. Keep API credentials out of code. Add only variable names/placeholders to `.env.example`.
7. Never claim endpoints, tests, data or skills worked unless you observed them working.
8. Ensure each UI chart has units, source, period, geography and explanatory notes.
9. Run the relevant automated checks before marking work done.
10. Update `docs/PROJECT_STATE.md` and record material choices in `docs/DECISIONS.md`.
