"""add wish.comments_num

Revision ID: 40795105a690
Revises: f8a31b15efbf
Create Date: 2017-06-20 16:41:06.804036

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '40795105a690'
down_revision = 'f8a31b15efbf'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('wish', sa.Column(
        'comments_num', sa.Integer(), nullable=True))


def downgrade():
    op.drop_column('wish', 'comments_num')
