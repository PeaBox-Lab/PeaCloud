import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
URL=os.getenv('PEACLOUD_DATABASE_URL','sqlite:///./peacloud.db')
engine=create_engine(URL,pool_pre_ping=True,connect_args={'check_same_thread':False} if URL.startswith('sqlite') else {})
SessionLocal=sessionmaker(bind=engine,autoflush=False,autocommit=False)
def init_db():
    with engine.begin() as c:
        c.execute(text('create table if not exists peacloud_meta (k varchar(100) primary key, v varchar(500) not null)'))
        c.execute(text("insert into peacloud_meta(k,v) values ('schema_version','1') on conflict(k) do nothing"))
def db_health():
    with engine.connect() as c:return c.execute(text('select 1')).scalar()==1
