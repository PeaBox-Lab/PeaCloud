# API Overview
Health: `GET /api/health`, `GET /api/liveness`, `GET /api/readiness`.
Inventory: `GET /api/resources`, `GET /api/inventory`, `GET /api/inventory/insights`.
Operations: `POST /api/resources/{id}/actions/{action}`, `GET /api/operations`.
Governance: `GET /api/approvals`, `GET /api/audit`.
Provisioning: `GET/POST /api/provisioning/plans`.
FinOps: `GET /api/costs/summary`, `GET /api/costs/recommendations`, `GET/POST /api/budgets`.
Production authentication remains a v0.12 gate. Do not expose the current header-role prototype to untrusted networks as an authorization mechanism.
