# PeaCloud v0.14 User Stories and Acceptance Criteria
1. **Tenant Admin:** I can assign a role only in my tenant. Acceptance: cross-tenant assignment is 403.
2. **Security:** I need database defense in depth. Acceptance: RLS policy covers principals and tenant_records and tenant repository sets transaction-local tenant context on PostgreSQL.
3. **SRE:** I need abuse protection. Acceptance: configurable per-key rate limiter returns 429 after the threshold.
4. **Auditor:** I need mutation evidence. Acceptance: mutation middleware appends hash-chained audit rows containing method/path/status without secrets.
5. **Platform Admin:** I can select managed secret storage. Acceptance: AWS Secrets Manager, Azure Key Vault, GCP Secret Manager and development environment backends share one interface.
6. **Security:** Secret listing must not expose values. Acceptance: secret status returns backend metadata only.
7. **Operator:** Routine actions remain protected by role and typed confirmation.
8. **Viewer:** Mutation remains denied.
9. **DBA:** Migration 002 is repeatable. Acceptance: clean DB upgrades through head.
10. **Contributor:** Cloud secret SDKs remain optional. Acceptance: core development doesn't require cloud packages.
11. **Customer:** Cost data remains visibly non-authoritative.
12. **Support:** Troubleshooting never requires raw tokens or secret exports.
13. **Maintainer:** Security-sensitive changes include negative authorization tests.
14. **Release Manager:** Release checklist includes tenant, RLS, rate-limit, audit and secret-backend validation.
15. **GRC:** Audit hash chain limitations are documented; external immutable retention remains a pre-GA gate.
