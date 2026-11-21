from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from app.jobs import queue
from app.observability import setup_logging, get_metrics, get_audit_log, log_event
from app.ratelimit import rate_limit_middleware
from typing import Optional

app = FastAPI(title='PeaCloud', version='0.17.0')
app.add_middleware(CORSMiddleware, allow_origins=['http://localhost:5173'], allow_methods=['*'], allow_headers=['*'])

@app.middleware("http")
async def rate_limit_middleware_wrapper(request: Request, call_next):
    return await rate_limit_middleware(request, call_next)

RES = [
    {'id': 'vm-01', 'name': 'payments-api', 'provider': 'AWS', 'type': 'Virtual machine', 'region': 'ap-south-1', 'state': 'running', 'tenant': 'demo'},
    {'id': 'vm-02', 'name': 'hr-platform', 'provider': 'Azure', 'type': 'Virtual machine', 'region': 'centralindia', 'state': 'stopped', 'tenant': 'demo'},
    {'id': 'db-01', 'name': 'customer-db', 'provider': 'GCP', 'type': 'Database', 'region': 'asia-south1', 'state': 'available', 'tenant': 'demo'},
    {'id': 'obj-01', 'name': 'pea-artifacts', 'provider': 'AWS', 'type': 'Object storage', 'region': 'ap-south-1', 'state': 'available', 'tenant': 'demo'}
]

def ctx(role: Optional[str], tenant: Optional[str]):
    return (role or 'operator', tenant or 'demo')

@app.get('/api/health')
def health():
    return {'status': 'ok', 'version': '0.17.0'}

@app.get('/api/metrics')
def metrics():
    return Response(content=get_metrics(), media_type="text/plain")

@app.get('/api/audit')
def audit(x_role: Optional[str] = Header(default='admin'), x_tenant: Optional[str] = Header(default='demo')):
    role, tenant = ctx(x_role, x_tenant)
    if role not in {'admin', 'auditor'}:
        raise HTTPException(403, 'Admin or auditor role required')
    return get_audit_log()

@app.get('/api/resources')
def resources(x_tenant: Optional[str] = Header(default='demo')):
    return [x for x in RES if x['tenant'] == x_tenant]

@app.get('/api/jobs')
def jobs(x_tenant: Optional[str] = Header(default='demo')):
    return queue.list(x_tenant)

@app.post('/api/jobs/{kind}')
def enqueue(kind: str, max_attempts: int = 3, idempotency_key: Optional[str] = None,
            x_role: Optional[str] = Header(default='operator'),
            x_tenant: Optional[str] = Header(default='demo'),
            priority: str = 'normal', metadata: Optional[dict] = None,
            request: Request = None):
    role, tenant = ctx(x_role, x_tenant)
    if role == 'viewer':
        raise HTTPException(403, 'Operator role required')
    if max_attempts < 1 or max_attempts > 10:
        raise HTTPException(400, 'max_attempts must be 1..10')
    if kind not in {'discovery', 'inventory-refresh', 'diagnostic', 'test-fail'}:
        raise HTTPException(400, 'Unsupported job type')
    j = queue.enqueue(kind, {'tenant': tenant}, max_attempts, idempotency_key, priority, metadata)
    log_event(user=x_role, action='job_enqueue', resource=j['id'], details={'kind': kind, 'tenant': tenant, 'priority': priority}, request=request)
    return j

@app.get('/api/jobs/{jid}')
def job(jid: str, x_tenant: Optional[str] = Header(default='demo')):
    j = queue.get(jid)
    if not j:
        raise HTTPException(404, 'Job not found')
    if j['payload']['tenant'] != x_tenant:
        raise HTTPException(403, 'Cross-tenant access denied')
    return j

@app.post('/api/jobs/{jid}/cancel')
def cancel(jid: str, x_role: Optional[str] = Header(default='operator'),
           x_tenant: Optional[str] = Header(default='demo'),
           request: Request = None):
    j = queue.get(jid)
    if not j:
        raise HTTPException(404, 'Job not found')
    if x_role == 'viewer':
        raise HTTPException(403, 'Operator role required')
    if j['payload']['tenant'] != x_tenant:
        raise HTTPException(403, 'Cross-tenant access denied')
    j = queue.cancel(jid)
    log_event(user=x_role, action='job_cancel', resource=jid, details={'tenant': x_tenant}, request=request)
    return j

@app.post('/api/jobs/{jid}/retry')
def retry(jid: str, x_role: Optional[str] = Header(default='operator'),
          x_tenant: Optional[str] = Header(default='demo'),
          request: Request = None):
    j = queue.get(jid)
    if not j:
        raise HTTPException(404, 'Job not found')
    if x_role == 'viewer':
        raise HTTPException(403, 'Operator role required')
    if j['payload']['tenant'] != x_tenant:
        raise HTTPException(403, 'Cross-tenant access denied')
    try:
        j = queue.retry(jid)
    except ValueError:
        raise HTTPException(400, 'Job not in dead_letter state')
    log_event(user=x_role, action='job_retry', resource=jid, details={'tenant': x_tenant}, request=request)
    return j

@app.post('/api/worker/run-one')
def run_one(x_role: Optional[str] = Header(default='admin')):
    if x_role != 'admin':
        raise HTTPException(403, 'Admin role required')
    from app.workers.worker import process_one
    return process_one() or {'status': 'idle'}

@app.get('/api/worker/status')
def worker_status():
    from app.workers.worker import get_status
    return get_status()