"""add email verification fields

Revision ID: 8cbd1c76448f
Revises: 39dae670e7e8
Create Date: 2025-10-16 08:43:58.452605

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8cbd1c76448f'
down_revision = '39dae670e7e8'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('member', schema=None) as batch_op:
        batch_op.add_column(sa.Column('email_verified', sa.Boolean(), nullable=False, server_default='false'))
        batch_op.add_column(sa.Column('verification_token', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('token_expires_at', sa.DateTime(), nullable=True))
        batch_op.create_unique_constraint(None, ['verification_token'])


def downgrade():
    with op.batch_alter_table('member', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')
        batch_op.drop_column('token_expires_at')
        batch_op.drop_column('verification_token')
        batch_op.drop_column('email_verified')
