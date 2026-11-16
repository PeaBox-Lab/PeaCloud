from uuid import uuid4
from datetime import datetime, timezone
SIZES={'small':{'cpu':2,'memory_gb':4},'medium':{'cpu':4,'memory_gb':8},'large':{'cpu':8,'memory_gb':16}}
COST_HINTS={'virtual_machine':{'small':35,'medium':70,'large':140},'object_storage':{'small':5,'medium':20,'large':60},'database':{'small':45,'medium':90,'large':180}}
def now():return datetime.now(timezone.utc).isoformat()
def plan(body):
    spec=body.model_dump(); tags={**spec['tags'],'env':spec['environment'],'managed-by':'peacloud'};spec['tags']=tags
    return {'id':str(uuid4()),'created_at':now(),'status':'planned','provider':spec['provider'],'resource_type':spec['resource_type'],'name':spec['name'],'region':spec['region'],'spec':spec,'changes':[{'op':'create','type':spec['resource_type'],'name':spec['name']}],'cost_estimate':{'currency':'USD','monthly_hint':COST_HINTS[spec['resource_type']][spec['size']],'authoritative':False},'risk':'high' if spec['environment']=='prod' else 'medium'}
def apply_mock(plan,provider):
    if plan['provider']!='mock':raise PermissionError('Real-provider provisioning is preview-only until the IaC runner is configured')
    return {'deployment_id':str(uuid4()),'status':'succeeded','provider':'mock','resource_name':plan['name'],'message':'Mock deployment applied safely','applied_at':now()}
