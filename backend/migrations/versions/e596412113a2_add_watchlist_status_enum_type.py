"""Add watchlist status enum type

Revision ID: e596412113a2
Revises: adb79d179304
Create Date: 2025-10-05 11:47:05.702770

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e596412113a2'
down_revision = '33b059164481'
branch_labels = None
depends_on = None


def upgrade():
    # Create the enum type
    op.execute("CREATE TYPE watchliststatus AS ENUM ('to_watch', 'watching', 'watched')")
    
def downgrade():
    op.execute("DROP TYPE watchliststatus")
