"""Rename user_id to member_id in watchlist and chat_message

Revision ID: 61d966ba4ea7
Revises: 8977d075fac1
Create Date: 2025-10-05 17:49:59.509449

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '61d966ba4ea7'
down_revision = '8977d075fac1'
branch_labels = None
depends_on = None


def upgrade():
    # Rename column in watchlist table
    with op.batch_alter_table('watchlist', schema=None) as batch_op:
        batch_op.alter_column('user_id', new_column_name='member_id')
    
    # Rename the foreign key constraint
    op.drop_constraint('watchlist_user_id_fkey', 'watchlist', type_='foreignkey')
    op.create_foreign_key('watchlist_member_id_fkey', 'watchlist', 'member', ['member_id'], ['id'], ondelete='CASCADE')
    
    # Add the unique constraint
    op.create_unique_constraint('watchlist_member_id_movie_id_key', 'watchlist', ['member_id', 'movie_id'])
    
    # Rename column in chat_message table
    with op.batch_alter_table('chat_message', schema=None) as batch_op:
        batch_op.alter_column('user_id', new_column_name='member_id')
    
    # Rename the foreign key constraint
    op.drop_constraint('chat_message_user_id_fkey', 'chat_message', type_='foreignkey')
    op.create_foreign_key('chat_message_member_id_fkey', 'chat_message', 'member', ['member_id'], ['id'], ondelete='CASCADE')


def downgrade():
    # Revert chat_message FK
    op.drop_constraint('chat_message_member_id_fkey', 'chat_message', type_='foreignkey')
    op.create_foreign_key('chat_message_user_id_fkey', 'chat_message', 'member', ['user_id'], ['id'], ondelete='CASCADE')
    
    # Revert chat_message column
    with op.batch_alter_table('chat_message', schema=None) as batch_op:
        batch_op.alter_column('member_id', new_column_name='user_id')
    
    # Revert watchlist unique constraint
    op.drop_constraint('watchlist_member_id_movie_id_key', 'watchlist', type_='unique')
    
    # Revert watchlist FK
    op.drop_constraint('watchlist_member_id_fkey', 'watchlist', type_='foreignkey')
    op.create_foreign_key('watchlist_user_id_fkey', 'watchlist', 'member', ['user_id'], ['id'], ondelete='CASCADE')
    
    # Revert watchlist column
    with op.batch_alter_table('watchlist', schema=None) as batch_op:
        batch_op.alter_column('member_id', new_column_name='user_id')