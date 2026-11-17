from fastapi import FastAPI,Header,HTTPException,Depends
from fastapi.middleware.cors import CORSMiddleware
from uuid import uuid4
from app.models import *
from app.core import *
from app.settings import settings
from app.auth.oidc import current_principal, require_role
from app.db.session import init_db, db_health
from app.tenancy.repository import ensure_schema,list_records,role_for,upsert_role
from app.security.rate_limit import limiter
from app.audit.sink import sink as audit_sink
from app.jobs.queue import queue as job_queue
from app.observability.telemetry import telemetry
from app.secrets.providers import backend as secret_backend
from contextlib import asynccontextmanager
@asynccontextmanager
async def lifespan(app):
    init_db();ensure_schema();yield
app=FastAPI(title='PeaCloud',version=settings.app_version,docs_url='/docs' if settings.docs_enabled else None,redoc_url=None,lifespan=lifespan);app.add_middleware(CORSMiddleware,allow_origins=list(settings.allowed_origins),allow_methods=['GET','POST','DELETE'],allow_headers=['Content-Type','X-Role','X-User'])
def role(x):return x or 'operator'

@app.middleware('http')
async def production_controls(request,call_next):
    key=(request.headers.get('X-Tenant') or 'anonymous')+':'+(request.client.host if request.client else 'local')
    limiter.check(key)
    response=await call_next(request)
    telemetry.record(response.status_code)
    if request.method in {'POST','PUT','PATCH','DELETE'}:
        audit_sink.write({'method':request.method,'path':request.url.path,'status':response.status_code,'tenant_hint':request.headers.get('X-Tenant','oidc')})
    return response

@app.get('/api/health')
def health():return {'status':'ok','version':settings.app_version,'safe_mode':True,'environment':settings.environment}

@app.get('/api/readiness')
def readiness():
    ok=db_health();return {'ready':ok,'checks':{'api':'ok','database':'ok' if ok else 'failed','inventory':'ok'},'version':settings.app_version}
@app.get('/api/liveness')
def liveness():return {'alive':True}


@app.get('/api/auth/status')
def auth_status(p=__import__('fastapi').Depends(current_principal)):
    return {'subject':p.subject,'role':p.role,'tenant':p.tenant,'mode':__import__('os').getenv('PEACLOUD_AUTH_MODE','dev-header')}
@app.get('/api/tenant/context')
def tenant_context(p=__import__('fastapi').Depends(current_principal)):
    return {'tenant_id':p.tenant,'isolation':'request-context','production_persistence':'postgresql-ready'}




@app.get('/api/observability/status')
def observability_status():return telemetry.snapshot()
@app.get('/api/jobs/status')
def jobs_status():return {'queue_mode':job_queue.mode}
@app.post('/api/jobs/{kind}')
def enqueue_job(kind:str,p=Depends(current_principal)):
    require_role(p,'operator');return job_queue.enqueue(kind,{'tenant':p.tenant,'subject':p.subject})
@app.get('/api/jobs/{job_id}')
def get_job(job_id:str,p=Depends(current_principal)):
    j=job_queue.get(job_id)
    if not j:raise HTTPException(404,'Job not found')
    if j.get('payload',{}).get('tenant')!=p.tenant:raise HTTPException(403,'Cross-tenant job read denied')
    return j

@app.get('/api/security/capabilities')
def security_capabilities():
    import os
    return {'rate_limit':{'requests':limiter.limit,'window_seconds':limiter.window,'mode':limiter.mode},'secret_backend':os.getenv('PEACLOUD_SECRET_BACKEND','environment'),'audit_sink':'hash-chained-jsonl','postgres_rls_tenant_context':True}
@app.post('/api/admin/roles/{tenant}/{subject}/{new_role}')
def assign_role(tenant:str,subject:str,new_role:str,p=Depends(current_principal)):
    require_role(p,'admin')
    if p.tenant!=tenant:raise HTTPException(403,'Cross-tenant role administration denied')
    if new_role not in {'viewer','operator','admin'}:raise HTTPException(400,'Invalid role')
    return upsert_role(subject,tenant,new_role)
@app.get('/api/admin/roles/{tenant}/{subject}')
def get_role(tenant:str,subject:str,p=Depends(current_principal)):
    require_role(p,'admin')
    if p.tenant!=tenant:raise HTTPException(403,'Cross-tenant role read denied')
    return {'tenant':tenant,'subject':subject,'role':role_for(subject,tenant)}
@app.get('/api/secrets/status')
def secrets_status(p=Depends(current_principal)):
    require_role(p,'admin');b=secret_backend();return {'backend':b.name,'values_exposed':False}

@app.get('/api/tenant/records/{kind}')
def tenant_records(kind:str,p=Depends(current_principal)):
    return {'tenant_id':p.tenant,'items':list_records(p.tenant,kind)}

@app.get('/api/resources')
def resources():return {'items':RESOURCES,'errors':{}}
@app.get('/api/inventory')
def inventory(provider:str|None=None,resource_type:str|None=None,q:str|None=None,offset:int=0,limit:int=50):
 x=RESOURCES
 if provider:x=[r for r in x if r['provider']==provider]
 if resource_type:x=[r for r in x if r['type']==resource_type]
 if q:x=[r for r in x if q.lower() in str(r).lower()]
 limit=min(max(limit,1),200);return {'items':x[offset:offset+limit],'total':len(x),'offset':offset,'limit':limit}
@app.get('/api/inventory/insights')
def insights():
 miss_owner=sum('owner' not in r['tags'] for r in RESOURCES);miss_env=sum('env' not in r['tags'] for r in RESOURCES)
 return {'total':len(RESOURCES),'coverage':{'owner_tag_percent':100*(len(RESOURCES)-miss_owner)/len(RESOURCES),'environment_tag_percent':100*(len(RESOURCES)-miss_env)/len(RESOURCES)},'findings':miss_owner+miss_env}
@app.post('/api/resources/{rid}/actions/{action}')
def act(rid:str,action:str,b:Action,x_user:str|None=Header(default='demo'),x_role:str|None=Header(default='operator')):
 r=next((x for x in RESOURCES if x['id']==rid),None)
 if not r:raise HTTPException(404,'Resource not found')
 if role(x_role)=='viewer':raise HTTPException(403,'Operator role required')
 expected=f'{action.upper()} {rid}'
 if b.confirmation!=expected:raise HTTPException(400,f'Confirmation must be exactly: {expected}')
 if action=='snapshot' and role(x_role)!='admin':
  a={'id':str(uuid4()),'resource_id':rid,'resource_name':r['name'],'action':action,'status':'pending','requested_by':x_user};APPROVALS.insert(0,a);audit(x_user,'approval.request',a['id']);return {'status':'pending_approval','approval_id':a['id']}
 if action=='start':r['state']='running'
 elif action=='stop':r['state']='stopped'
 elif action=='restart':r['state']='running'
 elif action!='snapshot':raise HTTPException(400,'Unsupported action')
 o={'id':str(uuid4()),'resource_id':rid,'action':action,'status':'succeeded'};OPS.insert(0,o);audit(x_user,'resource.action',f'{rid}:{action}');return o
@app.get('/api/operations')
def operations():return OPS
@app.get('/api/approvals')
def approvals():return APPROVALS
@app.get('/api/costs/summary')
def cost_summary():
 rows=costs();total=sum(x['monthly_cost'] for x in rows);alerts=[]
 for b in BUDGETS:
  pct=total/b['amount']*100
  if pct>=min(b['thresholds']):alerts.append({'budget':b['name'],'percent':round(pct,1),'severity':'critical' if pct>=100 else 'warning'})
 return {'currency':'USD','monthly_cost':total,'annualized_cost':total*12,'authoritative':False,'source':'mock-estimate','budget_alerts':alerts,'coverage_note':'Mock estimates only. Not provider billing data.'}
@app.get('/api/costs/recommendations')
def recs():return [{'resource_id':r['id'],'name':r['name'],'recommendation':'Review stopped VM for deallocation or deletion after retention checks','estimated_monthly_savings':8,'confidence':'low','automatic':False} for r in RESOURCES if r['type']=='virtual_machine' and r['state']=='stopped']
@app.get('/api/budgets')
def budgets():return BUDGETS
@app.post('/api/budgets')
def budget(b:BudgetIn,x_role:str|None=Header(default='operator')):
 if role(x_role)!='admin':raise HTTPException(403,'Admin role required')
 if b.amount<=0:raise HTTPException(400,'Budget must be > 0')
 x={'id':str(uuid4()),**b.model_dump()};BUDGETS.insert(0,x);return x
@app.post('/api/provisioning/plans')
def plan(b:ResourceIn,x_role:str|None=Header(default='operator')):
 if role(x_role)=='viewer':raise HTTPException(403,'Operator required')
 x={'id':str(uuid4()),'status':'planned','spec':b.model_dump(),'risk':'high' if b.environment=='prod' else 'medium','cost_estimate':{'authoritative':False,'monthly_hint':35}};PLANS.insert(0,x);return x
@app.get('/api/provisioning/plans')
def plans():return PLANS
@app.get('/api/system/capabilities')
def caps():return {'providers':['mock','aws','azure','gcp'],'features':['inventory','vm-actions','approvals','schedules','provisioning-plans','iac-preview-boundary','finops','budgets','audit'],'real_mutations_default':False}
@app.get('/api/audit')
def auditlog(x_role:str|None=Header(default='operator')):
 if role(x_role)!='admin':raise HTTPException(403,'Admin required')
 return AUDIT
