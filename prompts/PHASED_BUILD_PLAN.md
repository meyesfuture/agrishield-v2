# Phase-by-Phase Build Plan for the Coding Agent

Use one prompt/phase at a time. The active coding agent should inspect and act in the current workspace, not merely return code snippets in chat.

## Global setup instruction (paste once)

Read `AGENTS.md`, `README.md`, `docs/PRD.md`, `docs/ARCHITECTURE.md`, `docs/DATA_MANAGEMENT.md`, `docs/API_INTEGRATIONS.md`, `docs/UI_UX_SPEC.md`, `docs/PROJECT_STATE.md` and `docs/RESEARCH_AND_FEASIBILITY.md`. Inspect current code and environment. Preserve existing work. Discover installed skills and specifically check for Gravitas, Ponytail and applicable design/frontend/data/API/testing/security skills. Read their actual instructions before use. Never claim a skill was used if it was unavailable. Work phase-by-phase, run checks and update `docs/PROJECT_STATE.md` after each phase.

## Phase 0 — Reconnaissance

Inspect repository files, installed packages, runtime versions and existing app entry points. Inventory all files under `data/inbox/gemini_phase5/phase5_acquisition/`, inspect CSV headers/types/date coverage and JSON response structure, verify archive/source hashes against `PROVENANCE_MANIFEST.json`, read the acquisition report and reference reports, and generate `docs/research/PHASE0_RECONNAISSANCE.md`. Confirm existing code before selecting frameworks. Do not modify raw data. Audit skills with `docs/research/SKILL_AUDIT.md`. Finish with a concrete implementation plan and a list of mismatches. Stop and report if the workspace is not writable or expected files are missing.

## Phase 1 — Data validation and inventory

Write repeatable scripts to recompute every dataset's row count, columns, date range, commodity composition, null/zero counts, geographic coverage, unit labels, duplicate keys and SHA-256. Specifically prove that the arrival panel contains no wheat/paddy grain rows; verify paddy prices have null arrival quantities; preserve national stock granularity. Write `data/manifests/dataset_catalog.csv`, a quality report and the coverage matrix. Do not hardcode acquisition report counts in app code. Test outputs; update project state.

## Phase 2 — Application foundation

Use the existing repository's stack if present. Otherwise follow the architecture default. Build a maintainable app shell, routes, typography/design tokens, state patterns, error/empty/loading states, backend health and dataset-registry service. Ensure local start instructions are correct. No real model or hoarding score.

## Phase 3 — Data layer and endpoints

Implement schemas and services with fixture-driven tests. Start with local validated file reads or PostgreSQL only if appropriate. Implement dataset catalog, coverage, production/yield, prices, weather, procurement, stocks, district geometry and quality issue endpoints as needed. API source registry should report tested/blocked/not tested correctly. Do not live-call providers in the user request path.

## Phase 4 — Functional dashboard

Build Overview, Dataset Explorer, Production & Yield, Market Watch, Weather Context, Procurement & Stocks, District Map, Data Quality/Readiness and Methodology views. Bind all values to real validated data. Show missing fields and grain-arrival gap prominently. Add filters, units and source details. Provide accessible table equivalents where needed.

## Phase 5 — Premium visual implementation

Implement Apple-inspired restraint + Material clarity, controlled glassmorphism, excellent spacing/type, responsive information hierarchy, page transitions and subtle micro-interactions. Build one optimized custom 3D grain/silo hero in Three.js/React Three Fiber only if viable. Lazy-load it and provide static/reduced-motion fallbacks. Check Gravitas/Ponytail skills again if appropriate; record actual use. Avoid gratuitous or inaccessible animation.

## Phase 6 — Analytics/readiness

Build transparent data-quality metrics and source coverage. Only add statistical anomaly candidates if the required observation granularity/coverage passes. Do not implement grain arrival anomaly scoring using non-grain produce arrivals. Any synthetic what-if view must be clearly marked and excluded from real metrics.

## Phase 7 — Test, harden and package

Run backend tests, frontend tests, lint/typecheck, production build, data validation and end-to-end smoke tests. Review secrets, paths, exports, accessibility, responsive behavior, reduced motion, 3D fallback and error states. Test clean setup using documented commands. Produce `docs/research/FINAL_VERIFICATION_REPORT.md`, update README and PROJECT_STATE, and list every failure honestly.

## Resume prompt after a session reset

Read `docs/PROJECT_STATE.md` and the latest phase report first. Inspect git diff/status and current files. Do not redo completed work or assume unfinished work succeeded. Continue from the recorded `Next single action`, re-run relevant checks, and update the handoff file before ending.
