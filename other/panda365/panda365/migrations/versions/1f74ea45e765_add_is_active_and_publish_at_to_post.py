"""add is_active and publish_at to post

Revision ID: 1f74ea45e765
Revises: 5ad67785ca96
Create Date: 2017-04-26 17:28:40.186993

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy_utils import ArrowType


# revision identifiers, used by Alembic.
revision = '1f74ea45e765'
down_revision = '5ad67785ca96'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('post', sa.Column('is_active', sa.Boolean(), nullable=True))
    op.execute('UPDATE post SET is_active = true')
    op.alter_column('post', 'is_active', nullable=False)
    op.add_column('post', sa.Column('publish_at', ArrowType(), nullable=True))
    op.execute('UPDATE post SET publish_at = created_at')


def downgrade():
    op.drop_column('post', 'publish_at')
    op.drop_column('post', 'is_active')
