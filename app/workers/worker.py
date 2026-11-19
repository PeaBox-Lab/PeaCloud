import time
from app.jobs import queue
HANDLERS={'discovery':lambda p:{'message':'Discovery complete'},'inventory-refresh':lambda p:{'message':'Inventory refreshed'},'diagnostic':lambda p:{'message':'Diagnostics complete'},'test-fail':lambda p:(_ for _ in ()).throw(RuntimeError('Synthetic failure'))}
def process_one():
 j=queue.claim()
 if not j:return None
 try:
  if j['cancel_requested']:return queue.complete(j['id'],None)
  if j['kind'] not in HANDLERS:raise ValueError('Unknown job type')
  return queue.complete(j['id'],HANDLERS[j['kind']](j['payload']))
 except Exception as e:return queue.fail(j['id'],e)
def run():
 while True:
  if not process_one():time.sleep(1)
if __name__=='__main__':run()
