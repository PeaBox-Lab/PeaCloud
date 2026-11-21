import time
from loguru import logger
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request
from typing import Any, Dict, List, Optional

# Metrics
job_created = Counter('peacloud_jobs_created_total', 'Total jobs created', ['kind'])
job_succeeded = Counter('peacloud_jobs_succeeded_total', 'Total jobs succeeded', ['kind'])
job_failed = Counter('peacloud_jobs_failed_total', 'Total jobs failed', ['kind'])
job_duration = Histogram('peacloud_job_duration_seconds', 'Job duration in seconds', ['kind'])
active_jobs = Gauge('peacloud_active_jobs', 'Number of active jobs')

# Audit log store
audit_log: List[Dict[str, Any]] = []

def get_client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"

def log_event(user: Optional[str], action: str, resource: str, details: Dict[str, Any], request: Optional[Request] = None) -> None:
    entry = {
        'timestamp': time.time(),
        'user': user or 'anonymous',
        'action': action,
        'resource': resource,
        'details': details,
        'ip': get_client_ip(request) if request else None
    }
    audit_log.append(entry)
    logger.bind(audit=True).info(f"{action} {resource}", **details)

def get_metrics() -> bytes:
    return generate_latest()

def get_audit_log() -> List[Dict[str, Any]]:
    return audit_log

def setup_logging():
    logger.remove()
    logger.add(lambda msg: None, format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}", level="INFO")
    logger.add("app.log", rotation="10 MB", retention="14 days", level="DEBUG", backtrace=True, diagnose=True)