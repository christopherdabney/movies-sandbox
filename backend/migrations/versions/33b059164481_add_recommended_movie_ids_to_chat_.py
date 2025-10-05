"""Add recommended_movie_ids to chat_message

Revision ID: 33b059164481
Revises: c834d765f9f6
Create Date: 2025-10-04 21:11:33.848890

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '33b059164481'
down_revision = 'c834d765f9f6'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('chat_message', 
        sa.Column('recommended_movie_ids', postgresql.ARRAY(sa.Integer()), nullable=True)
    )


def downgrade():
    op.drop_column('chat_message', 'recommended_movie_ids')
