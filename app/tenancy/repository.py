from sqlalchemy import text
from app.db.session import engine
SCHEMA='''
create table if not exists tenants(id varchar(100) primary key,name varchar(200) not null,created_at varchar(64) not null);
create table if not exists principals(id varchar(200) not null,tenant_id varchar(100) not null,role varchar(32) not null,email varchar(320),primary key(id,tenant_id));
create table if not exists tenant_records(id varchar(100) primary key,tenant_id varchar(100) not null,kind varchar(50) not null,data text not null,created_at varchar(64) not null);
create index if not exists idx_tenant_records_scope on tenant_records(tenant_id,kind);
'''
def ensure_schema():
    with engine.begin() as c:
        for stmt in [x.strip() for x in SCHEMA.split(';') if x.strip()]:c.execute(text(stmt))
def _tenant_conn(tenant):
    c=engine.connect();tx=c.begin()
    if engine.dialect.name=='postgresql':c.execute(text("select set_config('peacloud.tenant_id',:t,true)"),{'t':tenant})
    return c,tx
def list_records(tenant,kind):
    c,tx=_tenant_conn(tenant)
    try:return [dict(x._mapping) for x in c.execute(text('select id,tenant_id,kind,data,created_at from tenant_records where tenant_id=:t and kind=:k'),{'t':tenant,'k':kind})]
    finally:tx.rollback();c.close()
def role_for(subject,tenant,default='viewer'):
    with engine.connect() as c:
        row=c.execute(text('select role from principals where id=:i and tenant_id=:t'),{'i':subject,'t':tenant}).fetchone();return row[0] if row else default
def upsert_role(subject,tenant,role,email=None):
    with engine.begin() as c:
        c.execute(text('delete from principals where id=:i and tenant_id=:t'),{'i':subject,'t':tenant});c.execute(text('insert into principals(id,tenant_id,role,email) values(:i,:t,:r,:e)'),{'i':subject,'t':tenant,'r':role,'e':email})
    return {'subject':subject,'tenant':tenant,'role':role}
