# Deployment & Operations

## Local-first development

The first target is a reliable local development setup on the project owner's Windows environment. Detect existing paths and package manager rather than assuming a specific drive. Do not place multi-gigabyte data in frontend public assets.

## Environment

Provide `.env.example` (not a real `.env`) naming only required configuration such as:

- `DATABASE_URL` (optional until PostgreSQL is wired)
- `DATA_ROOT` (default points to project data folder)
- provider-specific tokens only when legitimately acquired, e.g. `CEDA_API_TOKEN`
- allowed frontend/backend origin and service port settings as needed

Validate missing env values and provide a clear local error. Never require a paid service for the core demo. The UI should still start in data-file mode if a database isn't configured, but any fallback limitations must be visible.

## Data jobs

- Manual ingestion first; scheduled refresh is optional.
- Log start/end UTC, source, parameters, outcome, row count, schema version, checksum and error class.
- Do not continuously poll endpoints. Use reasonable intervals and provider terms.
- Preserve successful past data when a refresh fails; flag as stale rather than replacing with empty.
- Maintain backups for normalized database, but do not confuse backups with raw source archive.

## Deployment gate

Before public deployment, review data redistribution terms, exposed API routes, secrets, CORS, rate limiting, private coordinates and allegations. Prefer local/demo deployment until those reviews are complete.
