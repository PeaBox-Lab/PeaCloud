from datetime import datetime, timezone
from uuid import uuid4

def now(): return datetime.now(timezone.utc).isoformat()
def needs_approval(resource,action):
    return resource.tags.get('env','').lower() in {'prod','production'} or action in {'snapshot'}
def make_request(user,provider,resource,action):
    return {'id':str(uuid4()),'created_at':now(),'requested_by':user,'provider':provider,'resource_id':resource.id,'resource_name':resource.name,'action':action,'status':'pending','decision_by':None,'decision_at':None,'comment':''}
