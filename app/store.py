import json, os, sqlite3
from threading import RLock
class Store:
    def __init__(self,path=None):
        self.path=path or os.getenv('PEACLOUD_DB','peacloud.db'); self.lock=RLock()
        with self._db() as db:
            db.execute('create table if not exists records (kind text,id text primary key,data text not null)')
    def _db(self): return sqlite3.connect(self.path,check_same_thread=False)
    def list(self,kind):
        with self.lock,self._db() as db:return [json.loads(x[0]) for x in db.execute('select data from records where kind=? order by rowid desc',(kind,))]
    def put(self,kind,item):
        with self.lock,self._db() as db:db.execute('insert or replace into records(kind,id,data) values(?,?,?)',(kind,item['id'],json.dumps(item)));db.commit()
        return item
    def delete(self,kind,id):
        with self.lock,self._db() as db:
            row=db.execute('select data from records where kind=? and id=?',(kind,id)).fetchone()
            if row: db.execute('delete from records where kind=? and id=?',(kind,id));db.commit()
            return json.loads(row[0]) if row else None
