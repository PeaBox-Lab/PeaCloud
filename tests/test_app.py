from fastapi.testclient import TestClient
from app.main import app
c=TestClient(app)
def test_health():assert c.get('/api/health').json()['version']=='0.14.0'
def test_inventory():assert c.get('/api/inventory?limit=2').json()['total']==4
def test_rbac():assert c.post('/api/resources/vm-demo-01/actions/stop',headers={'X-Role':'viewer'},json={'confirmation':'STOP vm-demo-01'}).status_code==403
def test_action():assert c.post('/api/resources/vm-demo-01/actions/stop',json={'confirmation':'STOP vm-demo-01'}).status_code==200
def test_finops_label():assert c.get('/api/costs/summary').json()['authoritative'] is False
def test_budget_admin():assert c.post('/api/budgets',json={'name':'x','amount':10}).status_code==403
def test_liveness_readiness():
    assert c.get('/api/liveness').json()['alive'] is True
    assert c.get('/api/readiness').json()['ready'] is True
def test_cors_not_wildcard():
    from app.settings import settings
    assert '*' not in settings.allowed_origins
def test_auth_dev_context():
    r=c.get('/api/auth/status',headers={'X-Role':'operator','X-User':'alice','X-Tenant':'tenant-a'})
    assert r.status_code==200 and r.json()['role']=='operator' and r.json()['tenant']=='tenant-a'
def test_tenant_context():
    r=c.get('/api/tenant/context',headers={'X-Tenant':'tenant-b'})
    assert r.json()['tenant_id']=='tenant-b'
def test_readiness_database():
    r=c.get('/api/readiness');assert r.status_code==200 and r.json()['checks']['database']=='ok'
def test_tenant_records_scoped():
    from app.tenancy.repository import ensure_schema
    ensure_schema()
    r=c.get('/api/tenant/records/test',headers={'X-Tenant':'tenant-z'});assert r.status_code==200 and r.json()['tenant_id']=='tenant-z' and r.json()['items']==[]
def test_auth_defaults_development_only():
    import os
    assert os.getenv('PEACLOUD_AUTH_MODE','dev-header')=='dev-header'
def test_same_tenant_role_admin_and_cross_tenant_denied():
    h={'X-Role':'admin','X-User':'root','X-Tenant':'tenant-a'}
    r=c.post('/api/admin/roles/tenant-a/alice/operator',headers=h);assert r.status_code==200 and r.json()['role']=='operator'
    assert c.post('/api/admin/roles/tenant-b/bob/admin',headers=h).status_code==403
def test_security_capabilities_no_secrets():
    r=c.get('/api/security/capabilities');assert r.status_code==200 and r.json()['rate_limit']['requests']==120
    r=c.get('/api/secrets/status',headers={'X-Role':'admin','X-Tenant':'tenant-a'});assert r.json()['values_exposed'] is False
def test_rls_sql_principals_and_records():
    s=open('migrations/postgres_rls.sql').read();assert 'tenant_records_isolation' in s and 'principals_isolation' in s and 'current_setting' in s
