from fastapi import FastAPI,Header,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.jobs import queue
app=FastAPI(title='PeaCloud',version='0.16.0');app.add_middleware(CORSMiddleware,allow_origins=['http://localhost:5173'],allow_methods=['*'],allow_headers=['*'])
RES=[{'id':'vm-01','name':'payments-api','provider':'AWS','type':'Virtual machine','region':'ap-south-1','state':'running','tenant':'demo'},{'id':'vm-02','name':'hr-platform','provider':'Azure','type':'Virtual machine','region':'centralindia','state':'stopped','tenant':'demo'},{'id':'db-01','name':'customer-db','provider':'GCP','type':'Database','region':'asia-south1','state':'available','tenant':'demo'},{'id':'obj-01','name':'pea-artifacts','provider':'AWS','type':'Object storage','region':'ap-south-1','state':'available','tenant':'demo'}]
def ctx(role,tenant): return (role or 'operator',tenant or 'demo')
@app.get('/api/health')
def health():return {'status':'ok','version':'0.16.0'}
@app.get('/api/resources')
def resources(x_tenant:str|None=Header(default='demo')):return [x for x in RES if x['tenant']==x_tenant]
@app.get('/api/jobs')
def jobs(x_tenant:str|None=Header(default='demo')):return queue.list(x_tenant)
@app.post('/api/jobs/{kind}')
def enqueue(kind:str,max_attempts:int=3,idempotency_key:str|None=None,x_role:str|None=Header(default='operator'),x_tenant:str|None=Header(default='demo')):
 role,tenant=ctx(x_role,x_tenant)
 if role=='viewer':raise HTTPException(403,'Operator role required')
 if max_attempts<1 or max_attempts>10:raise HTTPException(400,'max_attempts must be 1..10')
 if kind not in {'discovery','inventory-refresh','diagnostic','test-fail'}:raise HTTPException(400,'Unsupported job type')
 return queue.enqueue(kind,{'tenant':tenant},max_attempts,idempotency_key)
@app.get('/api/jobs/{jid}')
def job(jid:str,x_tenant:str|None=Header(default='demo')):
 j=queue.get(jid)
 if not j:raise HTTPException(404,'Job not found')
 if j['payload']['tenant']!=x_tenant:raise HTTPException(403,'Cross-tenant access denied')
 return j
@app.post('/api/jobs/{jid}/cancel')
def cancel(jid:str,x_role:str|None=Header(default='operator'),x_tenant:str|None=Header(default='demo')):
 j=queue.get(jid)
 if not j:raise HTTPException(404,'Job not found')
 if x_role=='viewer':raise HTTPException(403,'Operator role required')
 if j['payload']['tenant']!=x_tenant:raise HTTPException(403,'Cross-tenant access denied')
 return queue.cancel(jid)
@app.post('/api/worker/run-one')
def run_one(x_role:str|None=Header(default='admin')):
 if x_role!='admin':raise HTTPException(403,'Admin role required')
 from app.workers.worker import process_one
 return process_one() or {'status':'idle'}
