"""add admin_votes_num

Revision ID: dbf55d071d34
Revises: 9cc8e9322d7e
Create Date: 2017-06-28 11:47:03.044287

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dbf55d071d34'
down_revision = '9cc8e9322d7e'
branch_labels = None
depends_on = None


def upgrade():
    """
    rename column `votes_num` to `real_votes_num`
    add column admin_votes_num
    """
    op.add_column(
        'wish', sa.Column(
            'admin_votes_num', sa.Integer(), server_default='0',
            nullable=True))
    op.add_column(
        'wish', sa.Column('real_votes_num', sa.Integer(), nullable=True))
    op.execute('UPDATE wish SET real_votes_num = votes_num')
    op.drop_column('wish', 'votes_num')


def downgrade():
    op.add_column('wish', sa.Column('votes_num', sa.INTEGER(), nullable=True))
    op.execute('UPDATE wish SET votes_num = real_votes_num')
    op.drop_column('wish', 'real_votes_num')
    op.drop_column('wish', 'admin_votes_num')
