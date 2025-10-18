"""add tokens_used to member

Revision ID: bed2b010bbbf
Revises: 8cbd1c76448f
Create Date: 2025-10-17 21:50:46.944983

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bed2b010bbbf'
down_revision = '8cbd1c76448f'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('member', schema=None) as batch_op:
        batch_op.add_column(sa.Column('tokens_used', sa.Integer(), nullable=False, server_default='0'))


def downgrade():
    with op.batch_alter_table('member', schema=None) as batch_op:
        batch_op.drop_column('tokens_used')