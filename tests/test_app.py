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
def test_snapshot_creates_approval_for_operator():
    r=c.post('/api/resources/mock/vm-demo-01/actions/snapshot',headers={'X-Role':'operator'},json={'confirmation':'SNAPSHOT vm-demo-01'})
    assert r.status_code==200 and r.json()['status']=='pending_approval'
    assert len(c.get('/api/approvals?status=pending').json())>=1
def test_approval_admin_only():
    r=c.post('/api/resources/mock/vm-demo-01/actions/snapshot',headers={'X-Role':'operator'},json={'confirmation':'SNAPSHOT vm-demo-01'})
    aid=r.json()['approval_id']
    assert c.post(f'/api/approvals/{aid}/decision',json={'decision':'approved'}).status_code==403
    assert c.post(f'/api/approvals/{aid}/decision',headers={'X-Role':'admin'},json={'decision':'approved','comment':'reviewed'}).status_code==200
def test_provisioning_preview_and_mock_apply():
    b={'provider':'mock','resource_type':'virtual_machine','name':'demo-new','region':'india-north','environment':'dev','size':'small'}
    r=c.post('/api/provisioning/plans',json=b); assert r.status_code==200; pid=r.json()['id']; assert r.json()['cost_estimate']['authoritative'] is False
    assert c.post(f'/api/provisioning/plans/{pid}/apply',json={'confirmation':'wrong'}).status_code==400
    assert c.post(f'/api/provisioning/plans/{pid}/apply',json={'confirmation':f'APPLY {pid}'}).status_code==200
def test_real_provider_apply_is_preview_only():
    b={'provider':'aws','resource_type':'virtual_machine','name':'preview','region':'ap-south-1','environment':'dev','size':'small'}
    r=c.post('/api/provisioning/plans',json=b); pid=r.json()['id']
    assert c.post(f'/api/provisioning/plans/{pid}/apply',json={'confirmation':f'APPLY {pid}'}).status_code==400
def test_iac_capabilities_safe_default():
    r=c.get('/api/provisioning/capabilities'); assert r.status_code==200; assert r.json()['iac']['real_apply_enabled'] is False
def test_terraform_preview_aws_vm():
    b={'provider':'aws','resource_type':'virtual_machine','name':'web-node','region':'ap-south-1','environment':'dev','size':'small'}
    p=c.post('/api/provisioning/plans',json=b).json(); r=c.get(f"/api/provisioning/plans/{p['id']}/iac-preview")
    assert r.status_code==200; assert 'aws_instance' in r.json()['configuration']; assert r.json()['validated'] is False
def test_real_iac_apply_remains_gated():
    b={'provider':'aws','resource_type':'virtual_machine','name':'gated','region':'ap-south-1','environment':'dev','size':'small'}
    p=c.post('/api/provisioning/plans',json=b).json(); pid=p['id']; r=c.post(f'/api/provisioning/plans/{pid}/apply',json={'confirmation':f'APPLY {pid}'})
    assert r.status_code==400; assert 'PEACLOUD_ALLOW_IAC_APPLY' in r.json()['detail']
