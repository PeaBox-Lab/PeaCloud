# Rate Limiting
Default is 120 requests per 60 seconds for each tenant/client key. Configure with `PEACLOUD_RATE_LIMIT` and `PEACLOUD_RATE_WINDOW_SECONDS`. The shipped limiter is per-process. Multi-replica production requires a shared Redis/API-gateway limiter before GA so limits cannot be bypassed by switching replicas.
