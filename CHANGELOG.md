# Changelog
## v0.7.0
- Added provisioning workspace with plan-before-apply workflow.
- Added persistent provisioning plans and deployment records.
- Added VM, object-storage and database blueprint previews.
- Added risk classification and explicitly non-authoritative cost hints.
- Added typed apply confirmation and production admin gate.
- Mock apply is functional; AWS/Azure/GCP remain preview-only until the IaC runner is configured.
- Preserved all prior features cumulatively.

## v0.6.0
- Added persistent change approval workflows.
- Added React Approvals workspace for admin review.
- Snapshot and production changes requested by operators now enter approval.
- Added approve/reject and approved-change execution APIs.
- Added approval audit records and storage diagnostics.
- Preserved all prior features cumulatively.

## v0.5.0
- Added SQLite persistence for profiles and schedules.
- Added React cloud connection wizard with provider-specific authentication methods.
- Added schedule execution engine with cron matching and policy checks.
- Added admin-only scheduler execution endpoint.
- Added storage diagnostics endpoint.
- Preserved all v0.1.0-v0.4.0 features cumulatively.

## v0.4.0
- Added automation schedules workspace to the React console.
- Added schedule create/list/delete REST APIs with RBAC.
- Added normalized resource-detail and capabilities API.
- Added explicit FinOps cost-summary integration boundary.
- Preserved all earlier functionality cumulatively.

## v0.3.0
- Rebuilt the GUI as React + TypeScript + Vite.
- Added responsive multi-cloud dashboard with provider inventory chart.
- Added searchable/filterable resource inventory and VM action controls.
- Added cloud connection cards and live connection testing.
- Added operation-history and governance workspaces.
- Added role selector, safety confirmations, loading states and notifications.
- Retained the v0.2.0 FastAPI provider, vault, RBAC and policy engine.

## v0.2.0
- Added named connection profiles for AWS, Azure, GCP and mock provider.
- Added secret vault API with authenticated encryption and non-disclosure of values.
- Added governance policy engine before every mutation.
- Added production-resource and protected-resource guardrails.
- Added Governance GUI workspace.
- Expanded tests for secrets, RBAC, profiles and policy controls.

## v0.1.0
- Initial multi-cloud dashboard, inventory, provider adapters, VM operations, audit and safe mock cloud.
