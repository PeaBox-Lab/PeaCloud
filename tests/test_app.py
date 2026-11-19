from fastapi.testclient import TestClient
from app.main import app
from app.jobs import Queue
import app.workers.worker as w
c=TestClient(app)
def test_health():assert c.get('/api/health').json()['version']=='0.16.0'
def test_viewer_denied():assert c.post('/api/jobs/diagnostic',headers={'X-Role':'viewer'}).status_code==403
def test_success():
 old=w.queue;q=Queue();w.queue=q
 try:j=q.enqueue('diagnostic',{'tenant':'t'});assert w.process_one()['status']=='succeeded'
 finally:w.queue=old
def test_retry_dead_letter():
 old=w.queue;q=Queue();w.queue=q
 try:
  j=q.enqueue('test-fail',{'tenant':'t'},2);x=w.process_one();assert x['status']=='queued';x['available_at']=0;x=w.process_one();assert x['status']=='dead_letter'
 finally:w.queue=old
def test_idempotency():
 q=Queue();a=q.enqueue('diagnostic',{'tenant':'t'},3,'k');b=q.enqueue('diagnostic',{'tenant':'t'},3,'k');assert a['id']==b['id']
def test_cancel_tenant():
 j=c.post('/api/jobs/diagnostic',headers={'X-Role':'operator','X-Tenant':'a'}).json()['id'];assert c.post(f'/api/jobs/{j}/cancel',headers={'X-Role':'operator','X-Tenant':'b'}).status_code==403;assert c.post(f'/api/jobs/{j}/cancel',headers={'X-Role':'operator','X-Tenant':'a'}).json()['status']=='cancelled'
def test_attempt_bounds():assert c.post('/api/jobs/diagnostic?max_attempts=11',headers={'X-Role':'operator'}).status_code==400
