"""replace tokens_used with agent_usage

Revision ID: 0a27267e67bb
Revises: bed2b010bbbf
Create Date: 2025-10-18 10:19:47.449389

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0a27267e67bb'
down_revision = 'bed2b010bbbf'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('member', schema=None) as batch_op:
        batch_op.add_column(sa.Column('agent_usage', sa.Numeric(precision=10, scale=6), nullable=False, server_default='0'))
        batch_op.drop_column('tokens_used')


def downgrade():
    with op.batch_alter_table('member', schema=None) as batch_op:
        batch_op.add_column(sa.Column('tokens_used', sa.INTEGER(), server_default=sa.text('0'), autoincrement=False, nullable=False), server_default='0')
        batch_op.drop_column('agent_usage')