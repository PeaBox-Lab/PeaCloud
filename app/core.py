from datetime import datetime,timezone
from uuid import uuid4
RESOURCES=[
 {'id':'vm-demo-01','provider':'mock','type':'virtual_machine','name':'payments-api','state':'running','region':'india-north','account':'demo','tags':{'env':'dev','owner':'platform'},'metadata':{'cpu':2,'memory_gb':8}},
 {'id':'vm-demo-02','provider':'mock','type':'virtual_machine','name':'hris-worker','state':'stopped','region':'india-north','account':'demo','tags':{'env':'test'},'metadata':{'cpu':2,'memory_gb':4}},
 {'id':'obj-demo-01','provider':'mock','type':'object_storage','name':'peaops-artifacts','state':'available','region':'india-south','account':'demo','tags':{'env':'shared'},'metadata':{'encrypted':True}},
 {'id':'db-demo-01','provider':'mock','type':'database','name':'peawork-db','state':'available','region':'india-north','account':'demo','tags':{'env':'dev'},'metadata':{'engine':'PostgreSQL 16'}}]
OPS=[];APPROVALS=[];SCHEDULES=[];BUDGETS=[];PLANS=[];AUDIT=[]
def now():return datetime.now(timezone.utc).isoformat()
def audit(user,event,detail):AUDIT.insert(0,{'timestamp':now(),'user':user,'event':event,'detail':detail})
def costs():
 rates={'virtual_machine':62,'object_storage':18,'database':95};rows=[]
 for r in RESOURCES:
  amt=8 if r['type']=='virtual_machine' and r['state']=='stopped' else rates[r['type']];rows.append({**r,'monthly_cost':amt,'authoritative':False})
 return rows
