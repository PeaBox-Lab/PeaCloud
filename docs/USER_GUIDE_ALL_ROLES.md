# PeaCloud v0.16.0 User Guide for All Roles
## Customer / Viewer
View dashboard and inventory. Viewer cannot create or cancel jobs. Cost views remain advisory.
## Operator / NOC
Use Workers to submit discovery, inventory-refresh, or diagnostic tasks. Record the job ID. Jobs retry with exponential backoff and bounded attempts. Use idempotency keys when repeating a client request.
## Admin / Tenant Admin
Admin can manually process one job in the development GUI. In production, run dedicated worker processes. Review dead letters and repeated failures. Do not place secrets in job payloads.
## SRE / DevOps
Run API and workers separately. Production worker command: `python -m app.workers.worker`. Configure Redis for multi-replica coordination. Monitor queued, running, succeeded, cancelled, and dead-letter states.
## Platform / Cloud Engineer
Only safe discovery/refresh/diagnostic handlers are enabled. Destructive cloud handlers require provider operation IDs, idempotency, rollback and compensation design first.
## Security / GRC
Job reads and cancellation are tenant scoped. Viewer cannot enqueue. Raw tokens, passwords and cloud keys must never enter payloads or errors.
## Developer / Contributor
Add handlers to `app/workers/worker.py`; handlers must be idempotent and return JSON-safe output. Tests must cover success, retry, dead letter, cancellation and tenant denial.
## Support / Customer Success
Collect job ID, kind, state, attempts, tenant, version and sanitized last error. Never ask for queue credentials.
## Maintainer / Release Manager
Require worker tests, updated docs/user stories, CI and security scans before release.
