"""change vote.uq constraint

Revision ID: 43c7ecf8ed02
Revises: 40795105a690
Create Date: 2017-06-21 14:19:42.577792

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy_utils import ArrowType

# revision identifiers, used by Alembic.
revision = '43c7ecf8ed02'
down_revision = '40795105a690'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('vote', sa.Column('count', sa.Integer(), nullable=True))
    op.execute('UPDATE vote SET count = 1')
    op.add_column('vote', sa.Column('updated_at', ArrowType(), nullable=True))
    op.execute('UPDATE vote SET updated_at = created_at')
    op.drop_column('vote', 'created_at')
    op.create_unique_constraint(
        'uq_vote_wish_user', 'vote', ['user_id', 'wish_id'])


def downgrade():
    op.drop_constraint('uq_vote_wish_user', 'vote', type_='unique')
    op.add_column('vote', sa.Column('created_at', ArrowType(), nullable=True))
    op.execute('UPDATE vote SET created_at = updated_at')
    op.drop_column('vote', 'updated_at')
    op.drop_column('vote', 'count')
