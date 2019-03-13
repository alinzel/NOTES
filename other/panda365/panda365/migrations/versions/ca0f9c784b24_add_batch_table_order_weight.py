"""empty message

Revision ID: ca0f9c784b24
Revises: 51083daea9cc
Create Date: 2017-07-25 14:28:07.391002

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ca0f9c784b24'
down_revision = '51083daea9cc'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('batch', sa.Column(
        'sort_weight', sa.Float(), server_default='0', nullable=True))
    op.add_column('game', sa.Column(
        'sort_weight', sa.Float(), server_default='0', nullable=True))


def downgrade():
    op.drop_column('game', 'sort_weight')
    op.drop_column('batch', 'sort_weight')
