# Identity and Tenancy Guide v0.13
Production mode is `PEACLOUD_AUTH_MODE=oidc`. Configure `PEACLOUD_OIDC_ISSUER`, `PEACLOUD_OIDC_AUDIENCE` and `PEACLOUD_OIDC_JWKS_URL`. Tokens must be RS256 and include `kid`, `sub`, `iat`, `exp`, tenant (`tenant_id` or `tid`) and `peacloud_role`. PeaCloud selects the matching RSA signing key from JWKS, validates signature/issuer/audience/time claims, and caches JWKS for five minutes. Unknown algorithms and missing tenants/roles fail closed.

Development `dev-header` mode exists only for trusted local development and must never be internet exposed.

Tenant repository queries scope by tenant ID. PostgreSQL RLS SQL is provided, but production GA still requires middleware/transaction code to set `SET LOCAL peacloud.tenant_id` for every DB transaction plus comprehensive cross-tenant negative tests.
