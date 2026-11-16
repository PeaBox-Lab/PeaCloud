from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime, timezone
from uuid import uuid4
from app.models import ActionRequest, ConnectionTest, ConnectionProfile, SecretInput, Operation
from app.security import SecretVault
from app.governance import PolicyEngine
from app.providers.mock import MockProvider
from app.providers.cloud import AWSProvider, AzureProvider, GCPProvider

app=FastAPI(title="PeaCloud",version="0.3.0")
providers={"mock":MockProvider(),"aws":AWSProvider(),"azure":AzureProvider(),"gcp":GCPProvider()}
operations=[]; audit=[]; profiles=[]
vault=SecretVault(); policy=PolicyEngine()

def now(): return datetime.now(timezone.utc).isoformat()
def role(x_role): return x_role or "operator"
def record(user,event,detail): audit.insert(0,{"timestamp":now(),"user":user,"event":event,"detail":detail})

@app.get("/api/health")
def health(): return {"status":"ok","version":"0.3.0","real_changes_enabled":False,"vault_ephemeral":vault.ephemeral}
@app.get("/api/connections")
def connections(): return [{"provider":n,"configured":n=="mock","mode":"demo" if n=="mock" else "environment"} for n in providers]
@app.get("/api/profiles")
def get_profiles(): return profiles
@app.post("/api/profiles")
def add_profile(body:ConnectionProfile,x_user:str|None=Header(default="demo@peacloud.local")):
    item=body.model_dump(); item["id"]=str(uuid4()); profiles.append(item); record(x_user,"profile.create",f"{body.provider}:{body.name}"); return item
@app.post("/api/secrets")
def add_secret(body:SecretInput,x_role:str|None=Header(default="operator")):
    if role(x_role)!="admin": raise HTTPException(403,"Admin role required")
    return vault.put(body.name,body.value)
@app.get("/api/secrets")
def secret_names(x_role:str|None=Header(default="operator")):
    if role(x_role)!="admin": raise HTTPException(403,"Admin role required")
    return {"names":vault.names(),"values_exposed":False}

@app.post("/api/connections/test")
def test_connection(body:ConnectionTest,x_user:str|None=Header(default="demo@peacloud.local")):
    try:
        result=providers[body.provider].test_connection(); record(x_user,"connection.test",body.provider); return result
    except Exception as e: raise HTTPException(400,str(e))
@app.get("/api/resources")
def resources(provider:str|None=None):
    names=[provider] if provider else list(providers)
    out=[]; errors={}
    for name in names:
        if name not in providers: raise HTTPException(404,"Provider not found")
        try: out += [x.model_dump() for x in providers[name].list_resources()]
        except Exception as e: errors[name]=str(e)
    return {"items":out,"errors":errors}
@app.get("/api/summary")
def summary():
    data=resources("mock")["items"]
    return {"providers":4,"connected":1,"resources":len(data),"running_vms":sum(x["type"]=="virtual_machine" and x["state"]=="running" for x in data),"alerts":0,"operations":len(operations)}
@app.post("/api/resources/{provider}/{resource_id}/actions/{action}")
def action(provider:str,resource_id:str,action:str,body:ActionRequest,x_user:str|None=Header(default="demo@peacloud.local"),x_role:str|None=Header(default="operator")):
    if role(x_role) not in {"operator","admin"}: raise HTTPException(403,"Operator role required")
    expected=f"{action.upper()} {resource_id}"
    if body.confirmation!=expected: raise HTTPException(400,f"Confirmation must be exactly: {expected}")
    if provider not in providers: raise HTTPException(404,"Provider not found")
    resource=next((x for x in providers[provider].list_resources() if x.id==resource_id),None)
    if not resource: raise HTTPException(404,"Resource not found")
    decision=policy.evaluate(action,resource,role(x_role))
    if not decision["allowed"]:
        record(x_user,"policy.block",f"{provider}:{resource_id}:{action}:"+"; ".join(decision["reasons"]))
        raise HTTPException(403,{"message":"Blocked by policy","reasons":decision["reasons"]})
    op=Operation(id=str(uuid4()),timestamp=now(),user=x_user,provider=provider,resource_id=resource_id,action=action,status="running",detail="")
    try:
        result=providers[provider].act(resource_id,action); op.status=result["status"];op.detail=result["message"]
    except PermissionError as e: op.status="blocked";op.detail=str(e)
    except Exception as e: op.status="failed";op.detail=str(e)
    operations.insert(0,op.model_dump());record(x_user,"resource.action",f"{provider}:{resource_id}:{action}:{op.status}")
    if op.status in {"failed","blocked"}: raise HTTPException(400,op.detail)
    return op
@app.get("/api/operations")
def get_operations(): return operations[:100]
@app.get("/api/audit")
def get_audit(x_role:str|None=Header(default="operator")):
    if role(x_role)!="admin": raise HTTPException(403,"Admin role required")
    return audit[:200]

app.mount("/static",StaticFiles(directory="app/static"),name="static")
@app.get("/")
def index(): return FileResponse("app/static/index.html")
