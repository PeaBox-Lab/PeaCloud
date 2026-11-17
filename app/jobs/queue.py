import json,os,time
from uuid import uuid4
class LocalQueue:
    mode='local';jobs={}
    def enqueue(self,kind,payload):
        j={'id':str(uuid4()),'kind':kind,'payload':payload,'status':'queued','created_at':time.time()};self.jobs[j['id']]=j;return j
    def get(self,id):return self.jobs.get(id)
class RedisQueue:
    mode='redis'
    def __init__(self):
        import redis
        self.r=redis.Redis.from_url(os.environ['PEACLOUD_REDIS_URL'],decode_responses=True)
    def enqueue(self,kind,payload):
        j={'id':str(uuid4()),'kind':kind,'payload':payload,'status':'queued','created_at':time.time()};self.r.set(f"peacloud:job:{j['id']}",json.dumps(j),ex=86400);self.r.rpush('peacloud:jobs',j['id']);return j
    def get(self,id):
        x=self.r.get(f'peacloud:job:{id}');return json.loads(x) if x else None
def create_queue():return RedisQueue() if os.getenv('PEACLOUD_REDIS_URL') else LocalQueue()
queue=create_queue()
