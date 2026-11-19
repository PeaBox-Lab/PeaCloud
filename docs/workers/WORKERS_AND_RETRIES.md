# Workers and Retries
Lifecycle: queued -> running -> succeeded. Failure requeues with exponential delay; after `max_attempts` the job enters `dead_letter`. Attempts are 1-10. Idempotency keys suppress duplicate active jobs. Cancellation is tenant-scoped and immediate for queued jobs. Safe built-in handlers: discovery, inventory-refresh, diagnostic. `test-fail` is solely for tests.
