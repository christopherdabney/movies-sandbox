"""change_watchlist_status_to_queued_watched

Revision ID: 4db19c45ae12
Revises: 61d966ba4ea7
Create Date: 2025-10-08 13:47:28.081304

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4db19c45ae12'
down_revision = '61d966ba4ea7'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Drop existing default first
    op.execute("ALTER TABLE watchlist ALTER COLUMN status DROP DEFAULT")
    
    # 2. Add new value to enum
    op.execute("ALTER TYPE watchliststatus ADD VALUE 'queued'")
    
    # 4. Recreate enum
    op.execute("ALTER TYPE watchliststatus RENAME TO watchliststatus_old")
    op.execute("CREATE TYPE watchliststatus AS ENUM ('queued', 'watched')")
    op.execute("ALTER TABLE watchlist ALTER COLUMN status TYPE watchliststatus USING status::text::watchliststatus")
    op.execute("DROP TYPE watchliststatus_old")
    
    # 5. Set new default
    op.execute("ALTER TABLE watchlist ALTER COLUMN status SET DEFAULT 'queued'::watchliststatus")


def downgrade():
    op.execute("ALTER TYPE watchliststatus RENAME TO watchliststatus_old")
    op.execute("CREATE TYPE watchliststatus AS ENUM ('to_watch', 'watching', 'watched')")
    op.execute("ALTER TABLE watchlist ALTER COLUMN status TYPE watchliststatus USING status::text::watchliststatus")
    op.execute("ALTER TABLE watchlist ALTER COLUMN status SET DEFAULT 'to_watch'")
    op.execute("DROP TYPE watchliststatus_old")
