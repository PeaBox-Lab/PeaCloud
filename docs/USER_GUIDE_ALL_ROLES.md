# PeaCloud v0.15.0 User Guide for All Roles
## Customer / Viewer
Use tenant-scoped inventory, health and advisory cost views. Viewer remains non-mutating. Never share credentials with Support.
## Operator / NOC
Routine cloud work requires correct tenant/resource context and typed confirmation. Long-running work should be sent to the job queue rather than tying up a request. Operators can create jobs; job reads are tenant isolated.
## Administrator / Tenant Admin
Admin controls roles and privileged workflows only within the signed tenant. Production requires OIDC/JWKS. Managed secret stores are preferred. Review rate-limit, queue and observability status before major changes.
## SRE / DevOps
Production Compose now uses PostgreSQL plus Redis. Redis provides a shared multi-replica limiter and job queue. Kubernetes deployment assets include two replicas, liveness/readiness probes, non-root/read-only security context, HPA 2-10 replicas at 70% CPU, and a PodDisruptionBudget.
## Platform / Cloud Engineer
Helm image defaults are placeholders. Replace `OWNER`, configure OIDC/database/Redis through Kubernetes Secrets or an external-secrets operator, and never put secrets in values.yaml. Use managed Redis/PostgreSQL for serious production.
## Observability / SRE
`/api/observability/status` exposes request/error counters and whether an OTLP endpoint is configured. v0.15 creates the OpenTelemetry dependency/configuration boundary; full trace/metric exporters and dashboards remain a later production gate.
## Security / GRC
Distributed Redis limiting prevents simple per-replica bypass. It does not replace edge WAF/API-gateway protection. Kubernetes containers run non-root with seccomp RuntimeDefault, all capabilities dropped, read-only root filesystem and no privilege escalation.
## DBA
PostgreSQL migrations/RLS remain mandatory. Redis persistence is not a system of record. Back up PostgreSQL/PITR and use managed Redis HA where queue loss matters.
## Developer / Contributor
Without `PEACLOUD_REDIS_URL`, PeaCloud falls back to local limiter/queue for development. Tests must verify tenant job isolation and production capabilities.
## FinOps
Cost estimates remain advisory/non-authoritative. No recommendation auto-executes.
## Support / Customer Success
Collect version, tenant, provider, region, resource ID/job ID, UTC time and sanitized error. Never collect bearer tokens, cloud keys, Redis/Postgres passwords or vault exports.
## Maintainer / Release Manager
Validate tests, migrations, Helm rendering/lint when available, container build, CodeQL, Scorecard and docs. Replace GitHub/registry `OWNER` placeholders before public release.
