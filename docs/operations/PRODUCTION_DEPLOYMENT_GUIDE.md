# PeaCloud v0.16.0 Production Deployment Guide

**Status:** Production-line / Pre-GA.

This Markdown companion summarizes the Word guide. Use the DOCX for the full runbook, tables, role ownership, rollout gates and checklists.

## Required architecture
- HTTPS load balancer/WAF or Nginx
- React GUI
- 2+ FastAPI replicas
- 2+ worker replicas
- Managed Redis 7+
- Managed PostgreSQL 16/17
- AWS Secrets Manager, Azure Key Vault, or GCP Secret Manager
- OpenTelemetry Collector and monitoring backend

## Minimum go-live gates
1. OIDC/JWKS with dev-header disabled.
2. Tenant isolation and PostgreSQL RLS negative tests.
3. Managed secrets and workload identity.
4. Worker retry, idempotency, cancellation and dead-letter tests.
5. Backups/PITR and restore drill.
6. Cloud sandbox tests and least privilege.
7. CodeQL, Dependabot, secret scanning and vulnerability reporting.
8. Rollback, on-call and incident runbook.

## Run
```bash
unzip peacloud-v0.16.0.zip
cd peacloud-v0.16.0
docker compose build --pull
docker compose up -d
```

## Worker
```bash
python -m app.workers.worker
```

## Production warning
Do not expose v0.16 publicly with development header authentication, in-memory queue state, wildcard CORS, embedded secrets, or without PostgreSQL/Redis and tenant negative tests.
