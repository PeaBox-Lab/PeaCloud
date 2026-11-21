import time
import json
import redis
from uuid import uuid4
from typing import Any, Dict, Optional, List
from threading import RLock
from app.observability import job_created, job_succeeded, job_failed, job_duration, active_jobs, log_event

TERMINAL = {'succeeded', 'failed', 'cancelled', 'dead_letter'}

# Priority ordering (higher number = higher priority)
PRIORITY_MAP = {'high': 3, 'normal': 2, 'low': 1}

class Queue:
    def __init__(self, redis_url: str = "redis://localhost:6379/0", fallback_to_memory: bool = True):
        self.jobs: Dict[str, Dict[str, Any]] = {}
        self.ready: List[str] = []  # list of job ids ready to be claimed
        self.lock = RLock()  # reentrant lock for thread safety
        self.fallback_to_memory = fallback_to_memory
        
        # Try to connect to Redis, fall back to memory-only if unavailable
        try:
            self.redis_client = redis.from_url(redis_url, socket_connect_timeout=2, socket_timeout=2)
            # Test connection
            self.redis_client.ping()
            self._using_redis = True
        except Exception:
            # Redis unavailable - use memory only
            self.redis_client = None
            self._using_redis = False
            # print("Redis unavailable - using in-memory queue only")

    def _redis_get_job(self, jid: str) -> Optional[Dict[str, Any]]:
        """Get job from Redis storage"""
        if not self._using_redis or not self.redis_client:
            return self.jobs.get(jid)
        try:
            job_key = f"job:{jid}"
            job_data = self.redis_client.get(job_key)
            if job_data:
                return json.loads(job_data)
        except Exception:
            pass
        return None

    def _redis_set_job(self, j: Dict[str, Any]):
        """Store job in Redis"""
        if not self._using_redis or not self.redis_client:
            self.jobs[j['id']] = j
            return
        try:
            job_key = f"job:{j['id']}"
            j_serialized = json.dumps(j)
            self.redis_client.set(job_key, j_serialized)
            if j['status'] == 'queued':
                self.redis_client.sadd('ready_queue', j['id'])
        except Exception:
            self.jobs[j['id']] = j

    def _redis_srem_ready(self, jid: str):
        """Remove job from ready queue in Redis"""
        if not self._using_redis or not self.redis_client:
            if jid in self.ready:
                self.ready.remove(jid)
            return
        try:
            self.redis_client.srem('ready_queue', jid)
        except Exception:
            if jid in self.ready:
                self.ready.remove(jid)

    def _redis_sadd_ready(self, jid: str):
        """Add job to ready queue in Redis"""
        if not self._using_redis or not self.redis_client:
            if jid not in self.ready:
                self.ready.append(jid)
            return
        try:
            self.redis_client.sadd('ready_queue', jid)
        except Exception:
            if jid not in self.ready:
                self.ready.append(jid)

    def _check_idempotency(self, key: str) -> Optional[Dict[str, Any]]:
        """Check if job with idempotency key exists and is not terminal"""
        if not key:
            return None
        # Check in-memory jobs first
        with self.lock:
            for j in self.jobs.values():
                if j.get('key') == key and j['status'] not in TERMINAL:
                    return j
        # If using Redis, check there too
        if self._using_redis and self.redis_client:
            try:
                existing_j = self.redis_client.hgetall(key)
                if existing_j and existing_j.get(b'status') not in [b'cancelled', b'dead_letter']:
                    return self._redis_deserialize_job(existing_j)
            except Exception:
                pass
        return None

    def _redis_deserialize_job(self, redis_data) -> Dict[str, Any]:
        """Deserialize job from Redis data"""
        if isinstance(redis_data, dict):
            redis_data = {k.decode('utf-8') if isinstance(k, bytes) else k: 
                          v.decode('utf-8') if isinstance(v, bytes) else v 
                          for k, v in redis_data.items()}
        job_id = redis_data.get('id')
        if job_id and job_id not in self.jobs:
            self.jobs[job_id] = redis_data
        return redis_data

    def enqueue(self, kind: str, payload: Dict[str, Any], max_attempts: int = 3,
                key: Optional[str] = None, priority: str = 'normal', metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        # Check idempotency without lock first
        existing = self._check_idempotency(key)
        if existing:
            return existing
            
        with self.lock:
            j = {
                'id': str(uuid4()),
                'kind': kind,
                'payload': payload,
                'status': 'queued',
                'attempts': 0,
                'max_attempts': max_attempts,
                'key': key,
                'created_at': time.time(),
                'available_at': time.time(),
                'last_error': None,
                'cancel_requested': False,
                'priority': priority,
                'metadata': metadata or {}
            }
            self.jobs[j['id']] = j
            self._add_to_ready(j)
            self._redis_set_job(j)
            job_created.labels(kind=kind).inc()
            return j

    def _add_to_ready(self, j: Dict[str, Any]) -> None:
        """Add job to ready queue based on availability."""
        with self.lock:
            j['available_at'] = time.time()
            self._redis_sadd_ready(j['id'])

    def claim(self) -> Optional[Dict[str, Any]]:
        with self.lock:
            if not self.ready:
                return None
            def priority_key(jid):
                job = self.jobs.get(jid, {})
                return PRIORITY_MAP.get(job.get('priority', 'normal'), 2)
            self.ready.sort(key=priority_key, reverse=True)
            jid = self.ready.pop(0)
            j = self.jobs[jid]
            j['status'] = 'running'
            j['attempts'] += 1
            self._redis_srem_ready(jid)
            return j

    def complete(self, i: str, result: Any):
        with self.lock:
            j = self.jobs[i]
            j['status'] = 'cancelled' if j['cancel_requested'] else 'succeeded'
            j['result'] = result
            j['completed_at'] = time.time()
            j['duration'] = j['completed_at'] - j['created_at']
            if j['status'] == 'succeeded':
                job_succeeded.labels(kind=j['kind']).inc()
            else:
                job_failed.labels(kind=j['kind']).inc()
            job_duration.labels(kind=j['kind']).observe(j['duration'])
            active_jobs.dec()
            return j

    def fail(self, i: str, e: Exception, base: int = 2):
        with self.lock:
            j = self.jobs[i]
            j['last_error'] = str(e)
            if j['attempts'] >= j['max_attempts']:
                j['status'] = 'dead_letter'
                job_failed.labels(kind=j['kind']).inc()
            else:
                j['status'] = 'queued'
                j['available_at'] = time.time() + base * 2 ** (j['attempts'] - 1)
                self._add_to_ready(j)
            active_jobs.dec()
            return j

    def cancel(self, i: str) -> Dict[str, Any]:
        with self.lock:
            j = self.jobs[i]
            j['cancel_requested'] = True
            if j['status'] == 'queued':
                j['status'] = 'cancelled'
            return j

    def get(self, i: str) -> Optional[Dict[str, Any]]:
        with self.lock:
            return self.jobs.get(i)

    def list(self, tenant: str):
        with self.lock:
            return [x for x in self.jobs.values() if x['payload']['tenant'] == tenant]

    def retry(self, i: str) -> Dict[str, Any]:
        with self.lock:
            j = self.jobs[i]
            if j['status'] != 'dead_letter':
                raise ValueError('Job not in dead_letter state')
            j['status'] = 'queued'
            j['attempts'] = 0
            j['available_at'] = time.time()
            self._add_to_ready(j)
            return j


queue = Queue()