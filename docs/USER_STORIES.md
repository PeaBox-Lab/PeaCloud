# PeaCloud v0.16 User Stories
1. Operator queues background work and receives a job ID.
2. SRE sees failed work retry with exponential backoff.
3. Poison work moves to dead letter after max attempts.
4. Duplicate active requests with one idempotency key return the same job.
5. Operator cancels a queued job in the same tenant.
6. Tenant B cannot read Tenant A's job.
7. Tenant B cannot cancel Tenant A's job.
8. Viewer cannot enqueue jobs.
9. Admin constrains attempts to 1-10.
10. Developer has a synthetic failure handler for retry tests.
11. DevOps runs worker independently from API.
12. Platform Engineer sees safe handlers only by default.
13. Customer retains a clear GUI for inventory and status.
14. Support diagnoses using sanitized job metadata.
15. Release Manager validates worker lifecycle and docs before release.

Each story is accepted when the corresponding automated RBAC/lifecycle/tenant test passes and the documented behavior is visible in the React Workers workspace.
