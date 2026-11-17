import os,time
from collections import defaultdict,deque
from threading import RLock
from fastapi import HTTPException
class RateLimiter:
    def __init__(self):
        self.window=int(os.getenv('PEACLOUD_RATE_WINDOW_SECONDS','60'));self.limit=int(os.getenv('PEACLOUD_RATE_LIMIT','120'));self.data=defaultdict(deque);self.lock=RLock()
    def check(self,key):
        now=time.time();cut=now-self.window
        with self.lock:
            q=self.data[key]
            while q and q[0]<cut:q.popleft()
            if len(q)>=self.limit:raise HTTPException(429,'Rate limit exceeded')
            q.append(now)
        return {'remaining':max(0,self.limit-len(q)),'window_seconds':self.window}
limiter=RateLimiter()
