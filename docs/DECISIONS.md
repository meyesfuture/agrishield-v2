# Architecture & Product Decision Log

Use one entry per material decision. Do not rewrite historical entries; add a superseding decision with a date.

## D-001 — Product claim
- Date: 2026-10-22
- Decision: Use `Punjab GrainWatch` / agricultural intelligence and supply-data readiness as the V1 product framing. Do not claim proven hoarding detection.
- Evidence: Phase 5 report says no wheat/paddy arrival quantity panel, no matched Punjab inventory balance, and no verified private-hoarding labels/controls.
- Revisit gate: actual comparable grain arrival observations, adequate stock/flow data, independently validated case dataset.

## D-002 — Source-drop treatment
- Decision: Keep extracted Gemini Phase 5 assets unchanged as an immutable evidence drop. Ingest by copy/manifest and write normalized outputs separately.
- Rationale: preserve raw data and allow audit/reprocessing.

## D-003 — Arrival/procurement accounting
- Decision: Treat mandi arrivals and procurement as potentially overlapping; never sum them as distinct supply without transaction-level reconciliation.

## D-004 — Geography
- Decision: Store original district/market names and mapping vintage. Use the 23-feature boundary GeoJSON only after verifying geometry/IDs; do not force uncertain historic splits.

## New decision template
### D-XXX — Short title
- Date:
- Decision:
- Alternatives:
- Evidence:
- Risks/limitations:
- Revisit conditions:
