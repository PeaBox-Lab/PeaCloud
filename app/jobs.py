import time
from uuid import uuid4
TERMINAL={'succeeded','failed','cancelled','dead_letter'}
class Queue:
 def __init__(self):self.jobs={};self.ready=[]
 def enqueue(self,kind,payload,max_attempts=3,key=None):
  if key:
   for j in self.jobs.values():
    if j.get('key')==key and j['status'] not in TERMINAL:return j
  j={'id':str(uuid4()),'kind':kind,'payload':payload,'status':'queued','attempts':0,'max_attempts':max_attempts,'key':key,'created_at':time.time(),'available_at':time.time(),'last_error':None,'cancel_requested':False};self.jobs[j['id']]=j;self.ready.append(j['id']);return j
 def get(self,i):return self.jobs.get(i)
 def list(self,tenant):return [x for x in self.jobs.values() if x['payload']['tenant']==tenant]
 def cancel(self,i):
  j=self.jobs[i];j['cancel_requested']=True
  if j['status']=='queued':j['status']='cancelled'
  return j
 def claim(self):
  for i in list(self.ready):
   j=self.jobs[i]
   if j['status']=='queued' and j['available_at']<=time.time():self.ready.remove(i);j['status']='running';j['attempts']+=1;return j
 def complete(self,i,result):
  j=self.jobs[i];j['status']='cancelled' if j['cancel_requested'] else 'succeeded';j['result']=result;return j
 def fail(self,i,e,base=2):
  j=self.jobs[i];j['last_error']=str(e)
  if j['attempts']>=j['max_attempts']:j['status']='dead_letter'
  else:j['status']='queued';j['available_at']=time.time()+base*2**(j['attempts']-1);self.ready.append(i)
  return j
queue=Queue()
