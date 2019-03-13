"""add is_bot in user

Revision ID: 3b12a5bb5842
Revises: 39348a7114e4
Create Date: 2017-07-28 17:11:34.333663

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3b12a5bb5842'
down_revision = '39348a7114e4'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('user', sa.Column('is_bot', sa.Boolean(), nullable=True))


def downgrade():
    op.drop_column('user', 'is_bot')
