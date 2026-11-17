# Cumulative Changelog
v0.1-v0.13 delivered multi-cloud management foundations, React, governance, schedules, approvals, provisioning/IaC boundary, inventory, FinOps, open-source engineering, OIDC/JWKS, PostgreSQL/Alembic and tenant/RLS foundations.
## v0.14.0
- Transaction-local PostgreSQL tenant context in tenant repository operations.
- RLS policies expanded to principals.
- Durable tenant role assignment/read endpoints with cross-tenant denial.
- AWS Secrets Manager, Azure Key Vault and GCP Secret Manager backend adapters.
- Configurable 120 requests/60 seconds default rate limiter.
- Hash-chained JSONL audit sink for mutation metadata.
- Migration 002 role index.
- Expanded docs and 15 acceptance-based user stories.
