# Production Runbook
v0.12 remains production-line/pre-GA.
## GitHub gate
Replace CODEOWNERS placeholder; protect `main`; require PR review, CI and CodeQL; enable dependency graph, Dependabot, secret scanning and Private Vulnerability Reporting; review OpenSSF Scorecard.
## Identity gate
Never run `dev-header` auth on a public endpoint. Configure OIDC issuer/audience and a JWKS verification implementation before internet exposure. Test Viewer, Operator, Admin and cross-tenant denial paths.
## Database gate
Use PostgreSQL production connection, external secrets, backups/PITR, monitoring and migration testing. SQLite is development-only.
## Runtime
Terminate HTTPS at a trusted load balancer/proxy. Use `/api/liveness` for process health and `/api/readiness` for traffic eligibility. Roll out immutable images using rolling or blue-green deployment.
## Incident
For suspected credential compromise disable provider permissions, preserve audit evidence, rotate credentials, use provider-native consoles as break-glass, and follow `SECURITY.md` for vulnerability handling.
