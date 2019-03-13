"""add spec and quantity in order

Revision ID: eed10b31d602
Revises: 3b12a5bb5842
Create Date: 2017-08-03 15:46:02.626999

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eed10b31d602'
down_revision = '3b12a5bb5842'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'order',
        sa.Column('quantity', sa.Integer(), server_default='1', nullable=True))
    op.add_column('order', sa.Column('spec', sa.Text(), nullable=True))


def downgrade():
    op.drop_column('order', 'spec')
    op.drop_column('order', 'quantity')
