# Security Model
## Trust boundaries
Browser -> PeaCloud API -> provider adapters / IaC boundary -> cloud provider APIs. Credentials remain server-side. The frontend must never receive provider access secrets.
## Controls
Least privilege; short-lived cloud identity; explicit mutation confirmation; approval separation; restrictive CORS; audit; non-root container; no-new-privileges/cap-drop in Compose; vulnerability policy; dependency/code scanning.
## Production gaps still open
OIDC/SAML authentication, durable PostgreSQL multi-tenant authorization, managed KMS/secret vault integration, rate limiting, immutable audit export, CSRF design if cookie sessions are added, real provider billing adapters, SBOM/provenance signatures, full end-to-end cloud sandbox tests and independent penetration testing are still required before calling the application fully production-ready.

## v0.12 identity/database boundary
OIDC and PostgreSQL boundaries are now represented in code. Production OIDC intentionally fails closed unless a verified-token adapter is configured. Tenant context exists but tenant-aware persistent resource tables and PostgreSQL RLS remain mandatory pre-GA work.
