"""security role indexes"""
from alembic import op
revision='002';down_revision='001';branch_labels=None;depends_on=None
def upgrade():op.create_index('idx_principals_tenant_role','principals',['tenant_id','role'])
def downgrade():op.drop_index('idx_principals_tenant_role',table_name='principals')
