import hashlib,json,os
from pathlib import Path
from threading import RLock
class AuditSink:
    def __init__(self):self.path=Path(os.getenv('PEACLOUD_AUDIT_FILE','audit.jsonl'));self.lock=RLock();self.prev='0'*64
    def write(self,event):
        body=json.dumps(event,sort_keys=True,separators=(',',':'));digest=hashlib.sha256((self.prev+body).encode()).hexdigest();row={'previous_hash':self.prev,'hash':digest,'event':event}
        with self.lock:
            with self.path.open('a',encoding='utf-8') as f:f.write(json.dumps(row,separators=(',',':'))+'\n')
            self.prev=digest
        return digest
sink=AuditSink()
