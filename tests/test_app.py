from fastapi.testclient import TestClient
from app.main import app
from app.jobs import Queue
c = TestClient(app)


def test_health(): 
    assert c.get('/api/health').json()['version'] == '0.17.0'

def test_viewer_denied(): 
    assert c.post('/api/jobs/diagnostic', headers={'X-Role': 'viewer'}).status_code == 403

def test_success(): 
    q = Queue() 
    j = q.enqueue('diagnostic', {'tenant': 't'}); 
    result = q.claim(); 
    result = q.complete(result['id'], 'done') 
    assert result['status'] == 'succeeded'

def test_retry_dead_letter(): 
    q = Queue() 
    j = q.enqueue('test-fail', {'tenant': 't'}, 2) 
    # first fail 
    result = q.claim(); 
    result = q.fail(result['id'], RuntimeError('boom')) 
    assert result['status'] == 'queued' 
    # second fail 
    result = q.claim(); 
    result = q.fail(result['id'], RuntimeError('boom')) 
    assert result['status'] == 'dead_letter'

def test_idempotency(): 
    q = Queue() 
    a = q.enqueue('diagnostic', {'tenant': 't'}, 3, 'k') 
    b = q.enqueue('diagnostic', {'tenant': 't'}, 3, 'k') 
    assert a['id'] == b['id']

def test_cancel_tenant(): 
    j = c.post('/api/jobs/diagnostic', headers={'X-Role': 'operator', 'X-Tenant': 'a'}).json()['id'] 
    assert c.post(f'/api/jobs/{j}/cancel', headers={'X-Role': 'operator', 'X-Tenant': 'b'}).status_code == 403 
    assert c.post(f'/api/jobs/{j}/cancel', headers={'X-Role': 'operator', 'X-Tenant': 'a'}).json()['status'] == 'cancelled'

def test_attempt_bounds(): 
    assert c.post('/api/jobs/diagnostic?max_attempts=11', headers={'X-Role': 'operator'}).status_code == 400

def test_priority_ordering(): 
    q = Queue() 
    q.enqueue('diagnostic', {'tenant': 't'}, max_attempts=3, priority='low') 
    q.enqueue('diagnostic', {'tenant': 't'}, max_attempts=3, priority='high') 
    q.enqueue('diagnostic', {'tenant': 't'}, max_attempts=3, priority='normal') 
    first = q.claim() 
    assert first['priority'] == 'high' 
    second = q.claim() 
    assert second['priority'] == 'normal' 
    third = q.claim() 
    assert third['priority'] == 'low'