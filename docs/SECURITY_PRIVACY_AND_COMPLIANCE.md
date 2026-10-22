# Security, Privacy & Responsible Use

## Secrets and access

- Store API keys/tokens in environment variables. Commit only `.env.example` with placeholder names.
- Ignore `.env`, private keys, local credentials, temporary exports and sensitive event coordinates in version control.
- Never print bearer tokens/cookies in logs; redact authorization headers and query secrets.
- Never bypass authentication, CAPTCHA, rate limits, certificate verification or access controls.
- Use documented and permissioned APIs, keep request rates reasonable and respect terms/licensing.

## Data and public claims

- Do not expose personally identifying or private commercial inventory data.
- Do not publish warehouse-level coordinates or actor names without lawful basis and explicit reviewed need.
- Keep allegation, inspection, seizure, charge, conviction, case dismissed and cleared records in separate legal-status classes.
- A stock discrepancy in government custody is not a private-hoarding label.
- A statistical outlier is not evidence of criminal intent.
- Clearly identify source dates, geographic level and limitations on all public-facing outputs.

## Application security

- Validate and constrain filters, date ranges, file paths and upload sizes.
- Restrict file reading to configured data roots; prevent path traversal.
- Use safe CSV exports and escape formulas when exporting untrusted text to spreadsheet-compatible formats.
- Add CORS restrictions appropriate to deployment, secure headers and dependency auditing.
- Keep API errors sanitized; detailed stack traces belong in local logs only.
- If public hosting is implemented, document data retention, access control, backups, secrets, security updates and takedown/contact path.
