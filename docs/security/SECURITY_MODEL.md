# Security Model
Tenant-isolated job reads/cancellation, bounded retries, idempotency and RBAC reduce worker risk. Destructive cloud handlers remain excluded until provider-specific idempotency and rollback exist.
