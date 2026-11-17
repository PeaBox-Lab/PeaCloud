"""tenant security tables"""
from alembic import op
import sqlalchemy as sa
revision='001';down_revision=None;branch_labels=None;depends_on=None
def upgrade():
 op.create_table('tenants',sa.Column('id',sa.String(100),primary_key=True),sa.Column('name',sa.String(200),nullable=False),sa.Column('created_at',sa.String(64),nullable=False))
 op.create_table('principals',sa.Column('id',sa.String(200),primary_key=True),sa.Column('tenant_id',sa.String(100),primary_key=True),sa.Column('role',sa.String(32),nullable=False),sa.Column('email',sa.String(320)))
 op.create_table('tenant_records',sa.Column('id',sa.String(100),primary_key=True),sa.Column('tenant_id',sa.String(100),nullable=False),sa.Column('kind',sa.String(50),nullable=False),sa.Column('data',sa.Text(),nullable=False),sa.Column('created_at',sa.String(64),nullable=False))
 op.create_index('idx_tenant_records_scope','tenant_records',['tenant_id','kind'])
def downgrade():
 op.drop_index('idx_tenant_records_scope',table_name='tenant_records');op.drop_table('tenant_records');op.drop_table('principals');op.drop_table('tenants')
