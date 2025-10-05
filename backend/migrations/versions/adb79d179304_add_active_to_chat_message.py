"""Add active to chat_message

Revision ID: adb79d179304
Revises: e596412113a2
Create Date: 2025-10-05 11:44:26.812340

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'adb79d179304'
down_revision = 'e596412113a2'
branch_labels = None
depends_on = None


def upgrade():
    # Add active column to chat_message
    op.add_column('chat_message', 
        sa.Column('active', sa.Boolean(), nullable=False, server_default='true')
    )


def downgrade():
    # Remove active column from chat_message
    op.drop_column('chat_message', 'active')