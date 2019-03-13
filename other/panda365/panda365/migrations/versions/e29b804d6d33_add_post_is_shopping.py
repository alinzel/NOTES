"""add post.is_shopping

Revision ID: e29b804d6d33
Revises: 42576c644618
Create Date: 2017-05-12 11:21:11.872665

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e29b804d6d33'
down_revision = '42576c644618'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('post', sa.Column('is_shopping', sa.Boolean(),
                                    server_default='false', nullable=True))


def downgrade():
    op.drop_column('post', 'is_shopping')
