"""polish price fields

Revision ID: 2dce049600fb
Revises: da73452142d0
Create Date: 2017-07-18 14:30:09.544842

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2dce049600fb'
down_revision = 'da73452142d0'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('batch', 'shipping_currency')
    op.drop_column('game', 'shipping_currency')
    op.add_column(
        'order', sa.Column('shipping_price', sa.DECIMAL(), nullable=True))
    op.execute('UPDATE "order" SET shipping_price = 0')
    op.alter_column('order', 'shipping_price', nullable=False)


def downgrade():
    op.drop_column('order', 'shipping_price')
    op.add_column(
        'game', sa.Column('shipping_currency', sa.Text(), nullable=False))
    op.add_column(
        'batch', sa.Column('shipping_currency', sa.Text(), nullable=False))
