"""add is_active in comment

Revision ID: 6621546d6ced
Revises: 502ba778db24
Create Date: 2017-08-10 11:19:57.164291

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6621546d6ced'
down_revision = '502ba778db24'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('comment', sa.Column('is_active',
                                       sa.Boolean(),
                                       server_default='true', nullable=True))


def downgrade():
    op.drop_column('comment', 'is_active')
