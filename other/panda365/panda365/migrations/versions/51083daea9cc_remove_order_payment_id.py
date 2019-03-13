"""remove order.payment_id

Revision ID: 51083daea9cc
Revises: 2dce049600fb
Create Date: 2017-07-22 12:30:04.864530

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '51083daea9cc'
down_revision = '2dce049600fb'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint(
        'fk_order_payment_id_payment', 'order', type_='foreignkey'
    )
    op.drop_column('order', 'payment_id')


def downgrade():
    op.add_column(
        'order', sa.Column('payment_id', sa.INTEGER(), nullable=True))
    op.create_foreign_key(
        'fk_order_payment_id_payment', 'order', 'payment',
        ['payment_id'], ['id']
    )
