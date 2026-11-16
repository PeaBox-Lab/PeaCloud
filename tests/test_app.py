from fastapi.testclient import TestClient
from app.main import app
c=TestClient(app)
def test_health(): assert c.get('/api/health').status_code==200
def test_mock_inventory():
    r=c.get('/api/resources?provider=mock'); assert r.status_code==200; assert len(r.json()['items'])>=4
def test_confirmation_guard():
    r=c.post('/api/resources/mock/vm-demo-01/actions/stop',json={'confirmation':'yes'}); assert r.status_code==400
def test_vm_action():
    r=c.post('/api/resources/mock/vm-demo-01/actions/stop',json={'confirmation':'STOP vm-demo-01'}); assert r.status_code==200
    data=c.get('/api/resources?provider=mock').json()['items']; assert next(x for x in data if x['id']=='vm-demo-01')['state']=='stopped'
def test_viewer_blocked():
    r=c.post('/api/resources/mock/vm-demo-01/actions/start',headers={'X-Role':'viewer'},json={'confirmation':'START vm-demo-01'}); assert r.status_code==403
