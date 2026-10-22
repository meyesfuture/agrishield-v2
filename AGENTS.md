# Instructions for AI coding agents

## Objective
Build Punjab GrainWatch as an honest, polished, reproducible agricultural intelligence application using the evidence actually present in this workspace.

## Non-negotiable rules

1. **Inspect first, modify second.** Inventory the repository, read the docs, inspect files in `data/inbox/gemini_phase5/phase5_acquisition/`, parse the manifests, and compare report claims against actual CSV/JSON contents.
2. **Do not fabricate.** No fake API successes, data rows, model metrics, citations, test results, stock observations, wheat/paddy arrivals, labels, or hoarding scores.
3. **Preserve originals.** Do not edit or overwrite Phase 5 source files. Compute/verify SHA-256 and write transformed outputs elsewhere.
4. **Distinguish evidence levels.** Use explicit statuses such as `observed`, `derived`, `synthetic demo`, `metadata only`, `blocked`, `stale`, and `missing`. Keep synthetic rows in `data/synthetic/` and always label them in UI.
5. **Do not equate absence with zero.** Null, explicit source zero, not reported, not applicable, and source error are separate states.
6. **No hoarding conclusions.** A statistical anomaly is only an investigation prompt. Without comparable grain arrivals, movement/stock data, and independently verified labels/controls, do not provide actor-level rankings or claims that hoarding is detected.
7. **No unsafe API shortcuts.** Never bypass CAPTCHA, authentication, paywalls, TLS validation or access restrictions. Do not disable certificate verification. Use legitimate credentials in environment variables only; never commit secrets.
8. **API claims need evidence.** Record the exact URL, request method, parameters, timestamp, response code, schema, pagination, units, source and checksum. Documentation is not proof that a route works.
9. **Inspect installed skills.** Discover available agent skills and read their actual files. Check specifically for Gravitas and Ponytail, plus relevant frontend/design, accessibility, API integration, data engineering, testing, performance and security skills. Use only skills that are actually installed/available and whose instructions fit the task. Do not claim a skill was used unless it was.
10. **Session persistence.** After each phase update `docs/PROJECT_STATE.md`, `docs/ROADMAP.md` if needed, and a phase report in `logs/phase_reports/`. Include current commit/status, commands run, tests, issues and the single next action.
11. **Read source reports.** Canonical specifications live in `docs/`; the files in `docs/research/source_reports/` are evidence/history. If reports conflict, preserve provenance and record the conflict in the decision log rather than silently reconciling it.
12. **Don't stop at a plan.** Once a phase is approved by its acceptance criteria, implement and test the deliverable before declaring it complete.

## Skill discovery procedure

- List installed skills and identify the file paths/entry instructions.
- Read applicable skills before design, code generation or test execution.
- Specifically search for `Gravitas`, `Ponytail`, and any installed UX/design-system, frontend, React/Astro, Three.js, API, Python, data validation, security and testing skills.
- If a named skill cannot be found, state `not found in current environment` in the skill audit; do not invent installation paths.
- Skill use is not a substitute for running tests and inspecting the actual application.

## UI quality bar

Aim for a premium combination of Apple's restrained typography, spacing, depth and micro-interactions with Google's Material clarity and accessible interaction states. Use glassmorphism sparingly where it improves hierarchy; ensure legibility, contrast and performance. A 3D grain/silo/field hero is required for the landing page, with a graceful static fallback if WebGL is unavailable. Motion should be coherent and purpose-driven, not a collection of distracting animations. Honour `prefers-reduced-motion` and keyboard interaction.

## Phase discipline

Follow `prompts/PHASED_BUILD_PLAN.md`. Do not jump to anomaly modelling before data validation gates pass. If the session is ending, write a precise handoff in `docs/PROJECT_STATE.md`.
