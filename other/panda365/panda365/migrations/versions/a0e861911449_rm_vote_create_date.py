"""rm vote.create_date

Revision ID: a0e861911449
Revises: b439579e6a18
Create Date: 2017-06-20 15:43:06.651966

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a0e861911449'
down_revision = 'b439579e6a18'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint('uq_vote_daily_per_user', 'vote', type_='unique')
    op.drop_column('vote', 'created_date')


def downgrade():
    op.add_column(
        'vote', sa.Column(
            'created_date', sa.DATE(), autoincrement=False, nullable=True))
    op.create_unique_constraint(
        'uq_vote_daily_per_user', 'vote',
        ['user_id', 'wish_id', 'created_date'])
