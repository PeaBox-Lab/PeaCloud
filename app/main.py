from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime, timezone
from uuid import uuid4
from app.models import ActionRequest, ConnectionTest, ConnectionProfile, SecretInput, Operation, ScheduleInput, ProfileWizardInput, ScheduleRunInput, ApprovalDecision
from app.security import SecretVault
from app.governance import PolicyEngine
from app.store import Store
from app.scheduler import run_due
from app.approvals import needs_approval, make_request
from app.providers.mock import MockProvider
from app.providers.cloud import AWSProvider, AzureProvider, GCPProvider

app=FastAPI(title="PeaCloud",version="0.6.0")
providers={"mock":MockProvider(),"aws":AWSProvider(),"azure":AzureProvider(),"gcp":GCPProvider()}
operations=[]; audit=[]; profiles=[]; schedules=[]
vault=SecretVault(); policy=PolicyEngine(); store=Store()
profiles=store.list("profile"); schedules=store.list("schedule"); approvals=store.list("approval")

def now(): return datetime.now(timezone.utc).isoformat()
def role(x_role): return x_role or "operator"
def record(user,event,detail): audit.insert(0,{"timestamp":now(),"user":user,"event":event,"detail":detail})

@app.get("/api/health")
def health(): return {"status":"ok","version":"0.6.0","real_changes_enabled":False,"vault_ephemeral":vault.ephemeral}
@app.get("/api/connections")
def connections(): return [{"provider":n,"configured":n=="mock","mode":"demo" if n=="mock" else "environment"} for n in providers]
@app.get("/api/profiles")
def get_profiles(): return profiles
@app.post("/api/profiles")
def add_profile(body:ConnectionProfile,x_user:str|None=Header(default="demo@peacloud.local")):
    item=body.model_dump(); item["id"]=str(uuid4()); profiles.append(item); store.put("profile",item); record(x_user,"profile.create",f"{body.provider}:{body.name}"); return item
@app.post("/api/secrets")
def add_secret(body:SecretInput,x_role:str|None=Header(default="operator")):
    if role(x_role)!="admin": raise HTTPException(403,"Admin role required")
    return vault.put(body.name,body.value)
@app.get("/api/secrets")
def secret_names(x_role:str|None=Header(default="operator")):
    if role(x_role)!="admin": raise HTTPException(403,"Admin role required")
    return {"names":vault.names(),"values_exposed":False}




@app.get("/api/approvals")
def get_approvals(status:str|None=None): return [x for x in approvals if not status or x["status"]==status]
@app.post("/api/approvals/{approval_id}/decision")
def decide_approval(approval_id:str,body:ApprovalDecision,x_user:str|None=Header(default="demo@peacloud.local"),x_role:str|None=Header(default="operator")):
    if role(x_role)!="admin": raise HTTPException(403,"Admin role required")
    item=next((x for x in approvals if x["id"]==approval_id),None)
    if not item: raise HTTPException(404,"Approval not found")
    if item["status"]!="pending": raise HTTPException(409,"Approval already decided")
    item["status"]=body.decision; item["comment"]=body.comment; item["decision_by"]=x_user; item["decision_at"]=now(); store.put("approval",item); record(x_user,"approval.decision",f"{approval_id}:{body.decision}"); return item
@app.post("/api/approvals/{approval_id}/execute")
def execute_approval(approval_id:str,x_user:str|None=Header(default="demo@peacloud.local"),x_role:str|None=Header(default="operator")):
    if role(x_role)!="admin": raise HTTPException(403,"Admin role required")
    item=next((x for x in approvals if x["id"]==approval_id),None)
    if not item: raise HTTPException(404,"Approval not found")
    if item["status"]!="approved": raise HTTPException(409,"Approval must be approved before execution")
    try: result=providers[item["provider"]].act(item["resource_id"],item["action"])
    except Exception as e: raise HTTPException(400,str(e))
    item["status"]="executed"; item["executed_at"]=now(); item["executed_by"]=x_user; store.put("approval",item); record(x_user,"approval.execute",approval_id); return {"approval":item,"result":result}

@app.post("/api/profiles/wizard")
def profile_wizard(body:ProfileWizardInput,x_user:str|None=Header(default="demo@peacloud.local"),x_role:str|None=Header(default="operator")):
    if role(x_role)!="admin": raise HTTPException(403,"Admin role required")
    guidance={
      "aws":{"sso":"Run aws configure sso, then aws sso login; set AWS_PROFILE for PeaCloud.","environment":"Use the boto3 credential chain; prefer short-lived role credentials."},
      "azure":{"managed_identity":"Deploy PeaCloud in Azure and assign a managed identity plus minimum Azure RBAC roles.","environment":"Use DefaultAzureCredential and AZURE_SUBSCRIPTION_ID."},
      "gcp":{"workload_identity":"Configure Workload Identity Federation and GCP_PROJECT_ID.","adc":"Run gcloud auth application-default login for local development."},
      "mock":{"environment":"No credentials required."}}
    item=body.model_dump(); item["id"]=str(uuid4()); item["created_at"]=now(); item["status"]="configured" if body.provider=="mock" else "pending_test"
    profiles.append(item); store.put("profile",item); record(x_user,"profile.wizard",f"{body.provider}:{body.auth_method}")
    return {"profile":item,"next_step":guidance.get(body.provider,{}).get(body.auth_method,"Configure the selected credential provider, then test the connection.")}
@app.post("/api/scheduler/run-due")
def scheduler_run(body:ScheduleRunInput,x_role:str|None=Header(default="operator")):
    if role(x_role)!="admin": raise HTTPException(403,"Admin role required")
    from datetime import datetime,timezone
    base=datetime.now(timezone.utc); dt=base.replace(minute=body.minute if body.minute is not None else base.minute,hour=body.hour if body.hour is not None else base.hour,day=body.day if body.day is not None else base.day,month=body.month if body.month is not None else base.month)
    return run_due(schedules,providers,policy,record,dt)
@app.get("/api/system/storage")
def storage_status(): return {"engine":"sqlite","path":store.path,"profiles":len(profiles),"schedules":len(schedules),"approvals":len(approvals),"persistent":True}

@app.get("/api/resources/{provider}/{resource_id}")
def resource_detail(provider:str,resource_id:str):
    if provider not in providers: raise HTTPException(404,"Provider not found")
    try: items=providers[provider].list_resources()
    except Exception as e: raise HTTPException(400,str(e))
    r=next((x for x in items if x.id==resource_id),None)
    if not r: raise HTTPException(404,"Resource not found")
    data=r.model_dump(); data["capabilities"]=["start","stop","restart","snapshot"] if r.type=="virtual_machine" else []
    data["estimated_monthly_cost"]={"currency":"USD","amount":0 if provider=="mock" else None,"status":"demo" if provider=="mock" else "provider-cost-integration-required"}
    return data
@app.get("/api/schedules")
def get_schedules(): return schedules
@app.post("/api/schedules")
def add_schedule(body:ScheduleInput,x_user:str|None=Header(default="demo@peacloud.local"),x_role:str|None=Header(default="operator")):
    if role(x_role) not in {"operator","admin"}: raise HTTPException(403,"Operator role required")
    if not body.cron.strip(): raise HTTPException(400,"Cron expression required")
    item=body.model_dump(); item["id"]=str(uuid4()); item["created_at"]=now(); schedules.append(item); store.put("schedule",item); record(x_user,"schedule.create",f"{body.provider}:{body.resource_id}:{body.action}:{body.cron}"); return item
@app.delete("/api/schedules/{schedule_id}")
def delete_schedule(schedule_id:str,x_user:str|None=Header(default="demo@peacloud.local"),x_role:str|None=Header(default="operator")):
    if role(x_role) not in {"operator","admin"}: raise HTTPException(403,"Operator role required")
    idx=next((i for i,x in enumerate(schedules) if x["id"]==schedule_id),None)
    if idx is None: raise HTTPException(404,"Schedule not found")
    item=schedules.pop(idx); store.delete("schedule",schedule_id); record(x_user,"schedule.delete",schedule_id); return item
@app.get("/api/costs/summary")
def cost_summary(): return {"currency":"USD","estimated_monthly":0,"covered_resources":len(providers["mock"].list_resources()),"status":"mock-only","note":"Real-provider billing APIs are not enabled in this release"}

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
    if needs_approval(resource,action) and role(x_role)!="admin":
        req=make_request(x_user,provider,resource,action); approvals.insert(0,req); store.put("approval",req); record(x_user,"approval.request",req["id"])
        return {"status":"pending_approval","detail":"Approval request created","approval_id":req["id"]}
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
