import os
from alembic import context
from sqlalchemy import engine_from_config,pool
config=context.config
url=os.getenv('PEACLOUD_DATABASE_URL')
if url:config.set_main_option('sqlalchemy.url',url.replace('%','%%'))
def offline():
 context.configure(url=config.get_main_option('sqlalchemy.url'),literal_binds=True);context.run_migrations()
def online():
 e=engine_from_config(config.get_section(config.config_ini_section),prefix='sqlalchemy.',poolclass=pool.NullPool)
 with e.connect() as c:context.configure(connection=c);context.run_migrations()
if context.is_offline_mode():offline()
else:online()
