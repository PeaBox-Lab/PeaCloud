import os,time
from collections import defaultdict,deque
from threading import RLock
from fastapi import HTTPException
class LocalLimiter:
    def __init__(self):self.window=int(os.getenv('PEACLOUD_RATE_WINDOW_SECONDS','60'));self.limit=int(os.getenv('PEACLOUD_RATE_LIMIT','120'));self.data=defaultdict(deque);self.lock=RLock();self.mode='local'
    def check(self,key):
        now=time.time();cut=now-self.window
        with self.lock:
            q=self.data[key]
            while q and q[0]<cut:q.popleft()
            if len(q)>=self.limit:raise HTTPException(429,'Rate limit exceeded')
            q.append(now);return {'remaining':self.limit-len(q),'window_seconds':self.window}
class RedisLimiter:
    def __init__(self):
        import redis
        self.limit=int(os.getenv('PEACLOUD_RATE_LIMIT','120'));self.window=int(os.getenv('PEACLOUD_RATE_WINDOW_SECONDS','60'));self.r=redis.Redis.from_url(os.environ['PEACLOUD_REDIS_URL'],decode_responses=True);self.mode='redis'
    def check(self,key):
        bucket=int(time.time())//self.window;k=f'peacloud:rate:{bucket}:{key}'
        with self.r.pipeline() as p:p.incr(k);p.expire(k,self.window*2);n,_=p.execute()
        if int(n)>self.limit:raise HTTPException(429,'Rate limit exceeded')
        return {'remaining':max(0,self.limit-int(n)),'window_seconds':self.window}
def create_limiter():
    if os.getenv('PEACLOUD_REDIS_URL'):return RedisLimiter()
    return LocalLimiter()
limiter=create_limiter()
