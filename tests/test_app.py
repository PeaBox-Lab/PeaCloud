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
def test_secret_admin_only():
    assert c.post('/api/secrets',json={'name':'x','value':'supersecret'}).status_code==403
    r=c.post('/api/secrets',headers={'X-Role':'admin'},json={'name':'x','value':'supersecret'}); assert r.status_code==200
    listed=c.get('/api/secrets',headers={'X-Role':'admin'}).json(); assert 'supersecret' not in str(listed); assert 'x' in listed['names']
def test_connection_profile():
    r=c.post('/api/profiles',json={'provider':'aws','name':'sandbox','account_id':'123'}); assert r.status_code==200
    assert any(x['name']=='sandbox' for x in c.get('/api/profiles').json())
def test_persistent_storage_status():
    r=c.get('/api/system/storage'); assert r.status_code==200; assert r.json()['persistent'] is True
def test_profile_wizard_admin():
    b={'provider':'mock','name':'local','auth_method':'environment'}
    assert c.post('/api/profiles/wizard',json=b).status_code==403
    assert c.post('/api/profiles/wizard',headers={'X-Role':'admin'},json=b).status_code==200
def test_scheduler_admin_only():
    assert c.post('/api/scheduler/run-due',json={}).status_code==403
