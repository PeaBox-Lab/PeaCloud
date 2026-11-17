# PeaCloud v0.15.0
Open-source multi-cloud control-plane project for AWS, Azure, GCP and extensible providers.

**Production-line / pre-GA.** v0.15 adds Redis shared rate limiting/job-queue foundations, hardened Kubernetes/Helm assets and observability groundwork. Critical cloud mutations should not yet depend on the job queue until dedicated workers, idempotency/retry/DLQ and external audit delivery are complete.

Documentation for every persona and current user stories are packaged under `docs/`.
