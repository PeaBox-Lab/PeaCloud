# PeaCloud v0.15 User Stories and Acceptance Criteria
1. **SRE:** I need rate limits shared across replicas. Acceptance: setting PEACLOUD_REDIS_URL selects Redis limiter mode.
2. **Operator:** I can submit a background job. Acceptance: Operator enqueue returns queued job ID.
3. **Security:** Tenant A cannot read Tenant B's queued job. Acceptance: cross-tenant job GET is 403.
4. **SRE:** I need deployable Kubernetes assets. Acceptance: chart includes Deployment, Service, HPA and PDB.
5. **Security:** Pods run hardened. Acceptance: runAsNonRoot, RuntimeDefault seccomp, read-only root, no privilege escalation and all capabilities dropped.
6. **Platform Engineer:** I can horizontally scale API. Acceptance: default 2 replicas, HPA max 10, target 70% CPU.
7. **SRE:** Kubernetes removes unhealthy pods from traffic. Acceptance: readiness and liveness probes call PeaCloud endpoints.
8. **DevOps:** Production Compose includes Redis health check and persistent volume.
9. **Observability engineer:** I can inspect application counters and OTLP configuration status.
10. **Admin:** Security capabilities reveal limiter mode but no credentials.
11. **Developer:** Local operation works without Redis through development fallback.
12. **Customer:** Cost guidance remains explicitly non-authoritative.
13. **Support:** Job troubleshooting uses job ID without requesting queue credentials.
14. **Maintainer:** Registry/chart owner placeholders must be replaced before public release.
15. **Release Manager:** Release documentation identifies OpenTelemetry exporters, external immutable audit and true worker execution as remaining production gates.
