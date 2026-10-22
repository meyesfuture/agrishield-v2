# Data Workspace

See `docs/DATA_MANAGEMENT.md` for full contracts. Put source evidence in `data/inbox/` first; the pipeline should copy/register it and preserve originals. Do not place secrets or sensitive personal data here.

- `inbox/gemini_phase5/phase5_acquisition/`: Phase 5 Gemini archive was extracted here as supplied.
- `inbox/other_reports/`: add any additional audits/reports here before the agent reviews them.
- `inbox/archives/`: preserve original ZIPs and export bundles.
- `raw/`: immutable pipeline-managed source snapshots.
- `processed/`: validated normalized outputs.
- `derived/`: explicit calculations/features.
- `synthetic/`: only labelled synthetic demo/test records.
- `manifests/`: inventory, coverage, hashes and run logs.
