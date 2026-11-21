# Product Roadmap – PeaCloud

## Market Analysis

Multi-cloud control planes are increasingly essential as organizations spread workloads across AWS, Azure, GCP and on-prem. Existing solutions (HashiCorp Terraform, AWS CloudControl, Azure Arc, Google Cloud Control Plane) provide infrastructure provisioning but fall short in:

- **Unified operations for existing resources** – there is no single place to inventory, monitor and action resources across clouds with a generic job-based model.
- **Self-service and multi-tenancy** – most enterprise tools require heavyweight setup; smaller teams need lightweight, extensible control planes.
- **Observability and auditability** – open-source alternatives like Cloud Custodian or Open Policy Agent cover policy but lack built-in metrics and audit trails.
- **Custom job types** – organizations need to run discovery, diagnostics, inventory refresh, custom scripts and third‑party actions from a common interface.

PeaCloud already delivers a working prototype with role‑based access, multi‑tenant filtering, idempotent job enqueue, retry/backoff, cancellation and dead‑letter handling. The roadmap below builds toward an enterprise‑grade control plane.

---

## Roadmap (18 months, 5 phases)

### Phase 0 – Discovery & Analysis (1 week, delivered)
- Codebase audit, market gap analysis, architecture review.
- Identify immediate low‑hanging fruit: metrics, structured logging, audit trail, job priorities.

### Phase 1 – Observability & Foundations (Weeks 2‑6)
**Goal:** Make PeaCloud production‑observable and extensible.

- **Prometheus metrics** (`/api/metrics`):
  - Counters: `peacloud_jobs_created_total{kind}`, `peacloud_jobs_succeeded_total{kind}`, `peacloud_jobs_failed_total{kind}`
  - Gauge: `peacloud_active_jobs`
  - Histogram: `peacloud_job_duration_seconds{kind}`
- **Structured JSON logging** to `app.log` with rotation and retention.
- **Immutable audit trail** stored in a dedicated in‑memory list with timestamp, user, action, resource, details, IP. Exposed via `/api/audit` for admin/auditor.
- **Enhanced job model**:
  - `priority`: low, normal, high
  - `metadata`: arbitrary JSON
  - `completed_at`, `duration` recorded for metrics and UI.
- **UI improvements**:
  - New **Analytics** tab showing metrics and audit log.
  - Job creation form with priority and metadata inputs.
  - Better role gating for UI actions.
- **Testing**: ensure all new endpoints pass `pytest`.

**Deliverables v0.17.0 (done):**
- `requirements.txt` extended with `prometheus-client` and `loguru`.
- `app/observability.py`: metrics and audit logging helpers.
- `app/jobs.py`: priority, metadata, duration metrics.
- `app/main.py`: `/api/metrics`, `/api/audit`, priority/metadata query params, audit logging.
- `app/workers/worker.py`: logs job start events.
- Frontend: Analytics page, audit table, job creation with priority/metadata.
- Tests pass.

### Phase 2 – Worker Resilience & Concurrency (Weeks 7‑12)
**Goal:** Harden job processing for production workloads.

- **Multi‑worker support**:
  - Allow `N` concurrent workers (configurable via env var `WORKER_COUNT`).
  - Add `/api/worker/status` exposing worker pool health.
  - Implement leader election or consistent hashing to distribute jobs.
- **Graceful shutdown**:
  - Handle `SIGTERM`/`SIGINT` to finish in‑flight jobs.
  - Drain queue before exit; log shutdown metrics.
- **Advanced retry policies**:
  - Configurable backoff multiplier and max jitter.
  - Per‑job timeout.
  - Compensation hooks on final failure.
- **Dead‑letter queue UI**:
  - List dead‑lettered jobs, allow manual retry (`POST /api/jobs/{id}/retry`).
  - Allow discarding dead‑lettered jobs.
- **Priority scheduling**:
  - Sort `ready` queue by priority before claiming jobs.
  - High priority jobs processed first.
- **Testing**:
  - Unit tests for priority ordering, retry policies, graceful shutdown.

**Deliverables v0.18.0 (done):**
- `app/workers/worker.py`: multi-threaded worker pool with graceful shutdown and Redis fallback.
- `app/jobs.py`: Redis-backed queue with in-memory fallback, priority scheduling, retry dead‑letter endpoint.
- `/api/worker/status` and `/api/jobs/{jid}/retry` endpoints.
- Tests updated to verify priority ordering, retry dead-letter, idempotency, cancellation.
- All tests pass.

### Phase 3 – Multi‑Tenant & Security Hardening (Weeks 13‑20)
**Goal:** Secure PeaCloud for enterprise tenants.

- **Fine‑grained RBAC**:
  - Define permissions: `job:create`, `job:cancel`, `job:read`, `worker:control`, `audit:read`.
  - Map roles to permission sets (viewer, operator, admin, auditor).
  - Implement decorator `@require_permission('job:cancel')` on endpoints.
- **Request signing & authentication**:
  - Optional JWT token verification via `Authorization: Bearer <token>`.
  - Token contains role, tenant, expiration.
  - If absent, fall back to X‑Role/X‑Tenant headers for development.
- **Rate limiting**:
  - Per‑tenant request limits (e.g., 100 requests/min).
  - Use `slowapi` or simple middleware.
- **Tenant quota & cost tracking**:
  - Track job count, resource count per tenant.
  - Expose `/api/tenants/{id}/usage` returning metrics.
  - Enforce quotas: reject job enqueue if quota exceeded.
- **Audit log immutability**:
  - Store audit log in append‑only storage (Redis list or file).
  - Add `/api/audit/verify` endpoint returning hash chain for tamper detection.
- **UI**:
  - Tenant management page (admin only) showing usage.
  - Permission‑aware navigation (hide menu items user cannot access).
- **Testing**:
  - Permission matrix tests.
  - Rate limiting tests.
  - JWT validation tests.

**Deliverables v0.19.0 (in progress):**
- Rate‑limiting middleware (`app/ratelimit.py`) with per‑tenant limits configurable via `RATE_LIMIT_PER_MINUTE` env var.
- Middleware registered in `app/main.py`.
- Tests verifying rate limiting and per‑tenant isolation.
- All existing tests pass.
- Next: implement RBAC, JWT auth, tenant quotas, audit immutability.

### Phase 4 – Orchestration & Workflow Engine (Weeks 21‑30)
**Goal:** Move from single jobs to complex workflows.

- **Workflow DSL**:
  - Define workflows as JSON/YAML with steps, dependencies, and conditionals.
  - Example:
    ```json
    {
      "name": "provision-vm",
      "steps": [
        {"id": "discover", "action": "discovery", "depends_on": []},
        {"id": "validate", "action": "diagnostic", "depends_on": ["discover"]},
        {"id": "create", "action": "create-resource", "depends_on": ["validate"]}
      ]
    }
    ```
- **Workflow engine**:
  - Evaluate dependency graph, schedule steps as jobs.
  - Maintain workflow status (`queued`, `running`, `succeeded`, `failed`, `cancelled`).
  - On step failure, optionally rollback previous steps.
- **Scheduled jobs**:
  - Support cron syntax for periodic jobs (e.g., `0 0 * * *` for nightly inventory refresh).
  - Use APScheduler or similar.
- **Event‑driven triggers**:
  - Webhooks that create jobs based on external events (e.g., CloudTrail events).
  - Endpoint: `POST /api/webhooks/{name}` with signature verification.
- **UI**:
  - **Workflow Designer**: drag‑and‑drop steps, configure dependencies.
  - **Workflow runs**: list, status, step timeline.
  - **Scheduler**: configure recurring jobs.
- **Testing**:
  - Workflow DAG execution tests.
  - Cron expression validation tests.

### Phase 5 – Integration & Extensibility (Weeks 31‑40)
**Goal:** Connect PeaCloud to the broader ecosystem.

- **Terraform provider**:
  - Allow provisioning PeaCloud resources via Terraform.
  - Define resources: `peacloud_job`, `peacloud_workflow`, `peacloud_tenant`.
- **Plugin system for job handlers**:
  - Allow loading custom handlers from `plugins/` directory.
  - Each plugin defines a `register_handlers()` function returning a dict of `{kind: callable}`.
  - Enable dynamic job types without modifying core code.
- **CI/CD pipeline support**:
  - Represent pipelines as workflows with steps (build, test, deploy).
  - Integrate with GitHub Actions, GitLab CI via webhooks.
- **Resource providers**:
  - Pluggable providers for AWS, Azure, GCP.
  - Implement `list_resources()`, `create_resource()`, `delete_resource()`.
  - Use to populate inventory dynamically instead of hardcoded `RES`.
- **Cost management dashboard**:
  - Integrate with cloud provider billing APIs.
  - Show cost per tenant, per resource.
  - Alerts when cost exceeds threshold.
- **UI**:
  - Plugin manager (install/uninstall plugins).
  - Provider configuration.
- **Testing**:
  - Terraform provider tests.
  - Plugin loading tests.

### Phase 6 – Enterprise Features (Weeks 41‑50)
**Goal:** Meet enterprise security and compliance requirements.

- **SSO / LDAP integration**:
  - OAuth2 / OIDC providers (Google, Azure AD, Okta).
  - SAML integration.
- **Compliance & governance**:
  - Policy as code with OPA (Open Policy Agent) integration.
  - Policy checks on job creation (e.g., restrict job types per role).
  - Signed releases (GPG signatures).
  - SBOM generation (SPDX/CycloneDX).
- **Multi‑region active‑active worker clusters**:
  - Deploy workers across regions.
  - Shared queue with Redis (replace in‑memory queue).
  - Failover handling.
- **Immutable audit log with external storage**:
  - Integrate with external log storage (Elasticsearch, Splunk).
  - Export audit logs via API.
- **User management**:
  - Add/remove users.
  - Reset passwords.
  - Role assignment.
- **UI**:
  - User management page.
  - Policy editor (OPA Rego).

### Phase 7 – Platform Maturity (18+ months)
**Goal:** Build a thriving open‑source platform.

- **Serverless function support**:
  - Execute user‑provided code snippets as jobs (sandboxed container).
- **Event‑driven architecture**:
  - Introduce message bus (Kafka, NATS) for decoupling.
  - Workers subscribe to topics.
- **Marketplace**:
  - Third‑party providers and job handlers.
  - Community contributions.
- **Multi‑cloud abstraction layer**:
  - Unified API for resource types (compute, storage, database, network).
  - Map to provider‑specific APIs.
- **Documentation & community**:
  - Extensive documentation, tutorials.
  - GitHub discussions, issue templates.

---

## Summary

- **Phase 1 (v0.17)** delivered observability, audit logging, job priorities, UI enhancements.
- **Phase 2 (v0.18)** delivered worker concurrency, graceful shutdown, Redis fallback, priority scheduling, dead‑letter retry, rate limiting foundation.
- **Phase 3 (v0.19)** started with rate limiting middleware and tests; next is RBAC, JWT, tenant quotas.
- **Phases 4‑5** focus on orchestration, workflows, integrations, Terraform provider, plugin system.
- **Phases 6‑7** target enterprise readiness and ecosystem growth.

The roadmap is designed to be incremental: each phase builds on the previous one, and the existing tests ensure backward compatibility. The first production‑ready release after Phase 1 (v0.17) can be deployed with monitoring and audit capabilities.

## Immediate Next Steps (to continue Phase 3)

1. Implement RBAC (permissions, role mapping).
2. Add JWT authentication (optional Bearer token).
3. Implement tenant quota tracking (`/api/tenants/{id}/usage`).
4. Add audit log immutability (`/api/audit/verify`).
5. Update UI for tenant management and permission‑aware navigation.
6. Add tests for RBAC and quotas.
7. Update `README.md` with new features and configuration options.