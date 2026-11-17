# PeaCloud v0.14.0 User Guide for All Roles
## Customer / Viewer
View tenant inventory, health and advisory FinOps data. Viewer cannot mutate infrastructure. Never submit credentials to support.
## Operator / NOC
Validate tenant, owner, environment, resource ID and impact. Typed confirmation remains mandatory. Use approval flows for high-risk/production changes.
## Administrator / Tenant Admin
Production uses validated OIDC. Admin can assign Viewer/Operator/Admin roles only inside the Admin's own tenant. Review role changes and audit evidence. Configure managed secret backend instead of environment secrets for mature production deployments.
## SRE / DevOps
Rate limiting defaults to 120 requests per 60 seconds per tenant/client key and is configurable. Mutating API requests produce hash-chained JSONL audit evidence. Readiness includes database health. PostgreSQL tenant transactions set `peacloud.tenant_id` using transaction-local context in tenant repository operations.
## Security / GRC
RLS SQL covers tenant_records and principals. Test Tenant A -> Tenant B denial in real PostgreSQL before GA. Audit hash chaining detects alteration order but is not a substitute for external WORM/immutable storage. Send production audit data to a write-protected SIEM/object store in the next deployment layer.
## Cloud / Platform Engineer
Secret backend adapters now exist for AWS Secrets Manager, Azure Key Vault and Google Secret Manager. Use provider-native workload identity/managed identity rather than embedded credentials. Secret values never have a listing API.
## DBA
Alembic migration 002 adds tenant/role indexing. Apply migration, RLS policies and backup/restore tests in staging before production.
## Developer / Contributor
Local environment secret backend and SQLite remain development defaults. Keep provider packages optional. Add negative authorization and tenant tests to every security-sensitive PR.
## FinOps / Finance
Costs remain advisory/non-authoritative until actual provider billing connectors arrive. No recommendation auto-executes.
## Support / Customer Success
Collect version, tenant, provider, region, resource ID, UTC time and sanitized error. Never collect JWTs, cloud keys, passwords, vault exports or database credentials.
## Maintainer / Release Manager
Require CI, CodeQL, migration checks, Scorecard review and updated role/user-story docs. Publish known production gaps openly.
