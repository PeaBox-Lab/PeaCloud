# PeaCloud v0.14.0
Open-source multi-cloud control-plane project for AWS, Azure, GCP and extensible providers.

**Production-line / pre-GA.** v0.14 advances tenant isolation, durable roles, managed secret backends, abuse controls and audit evidence. It is not GA: shared/distributed rate limiting, external immutable audit delivery and real PostgreSQL cross-tenant attack testing remain required.

## Highlights
RS256/JWKS OIDC; PostgreSQL/Alembic; transaction tenant context; RLS policy for tenant records/principals; same-tenant admin role management; AWS/Azure/GCP secret backend adapters; 120 req/60 sec configurable limiter; hash-chained mutation audit; comprehensive documentation/user stories.

## Docs
Start with `docs/USER_GUIDE_ALL_ROLES.md`, `docs/USER_STORIES.md`, `docs/security/SECURITY_MODEL.md`, `docs/secrets/SECRET_BACKENDS.md`, `docs/audit/AUDIT_GUIDE.md` and `docs/release/RELEASE_CHECKLIST.md`.
