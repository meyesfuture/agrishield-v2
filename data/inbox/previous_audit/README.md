# Optional Previous Audit Archive

If you want the coding agent to inspect the older `Punjab_Grain_Hoarding_Intelligence_Audit*.zip` / `sept` data bundle too, copy that ZIP into `data/inbox/archives/` and extract it into this folder without overwriting the Phase 5 source drop.

Keep old and new acquisition runs separate. The agent must compare dates, manifests, hashes and actual rows before treating the older data as valid/current. In particular, an old report claiming a large FCI record count must not be accepted unless those corresponding files are physically present and validated. This folder is a convenience for older evidence, not a requirement to start implementing the descriptive dashboard.
