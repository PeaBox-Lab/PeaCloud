import time
import os
from collections import defaultdict, deque
from threading import Lock
from fastapi import Request, HTTPException

rate_limit_buckets = defaultdict(deque)
lock = Lock()

def get_rate_limit_per_minute() -> int:
    return int(os.getenv('RATE_LIMIT_PER_MINUTE', '100'))

def check_rate_limit(tenant: str, limit_per_minute: int = None) -> bool:
    """Return True if the request is allowed, False if rate limit exceeded."""
    if limit_per_minute is None:
        limit_per_minute = get_rate_limit_per_minute()
    now = time.time()
    with lock:
        bucket = rate_limit_buckets[tenant]
        while bucket and bucket[0] < now - 60:
            bucket.popleft()
        if len(bucket) >= limit_per_minute:
            return False
        bucket.append(now)
        return True

async def rate_limit_middleware(request: Request, call_next):
    """FastAPI middleware that enforces per-tenant rate limits."""
    tenant = request.headers.get('X-Tenant', 'demo')
    if not check_rate_limit(tenant):
        raise HTTPException(status_code=429, detail='Rate limit exceeded')
    response = await call_next(request)
    return response