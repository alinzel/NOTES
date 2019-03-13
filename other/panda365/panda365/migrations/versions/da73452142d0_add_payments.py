"""add payments

Revision ID: da73452142d0
Revises: 964367f66eee
Create Date: 2017-07-17 16:58:37.006682

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy_utils import ArrowType, CurrencyType

# revision identifiers, used by Alembic.
revision = 'da73452142d0'
down_revision = '964367f66eee'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'payment',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', ArrowType(), nullable=True),
        sa.Column('updated_at', ArrowType(), nullable=True),
        sa.Column('method', sa.Text(), nullable=True),
        sa.Column('amount', sa.DECIMAL(), nullable=False),
        sa.Column('currency', CurrencyType(length=3), nullable=False),
        sa.Column('status', sa.SmallInteger(), nullable=True),
        sa.Column('vendor', sa.SmallInteger(), nullable=False),
        sa.Column('transaction_id', sa.Text(), nullable=True),
        sa.Column('ref_id', sa.Text(), nullable=True),
        sa.Column('object_type', sa.Text(), nullable=False),
        sa.Column('object_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('extra_data', JSONB(), nullable=True),
        sa.Column('return_url', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ['user_id'], ['user.id'], name=op.f('fk_payment_user_id_user')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_payment'))
    )
    op.add_column('order', sa.Column(
        'currency', CurrencyType(length=3), nullable=False))
    op.add_column('order', sa.Column(
        'payment_id', sa.Integer(), nullable=True))
    op.add_column('order', sa.Column('price', sa.DECIMAL(), nullable=False))
    op.create_foreign_key(
        op.f('fk_order_payment_id_payment'), 'order', 'payment',
        ['payment_id'], ['id'])


def downgrade():
    op.drop_constraint(
        op.f('fk_order_payment_id_payment'), 'order', type_='foreignkey')
    op.drop_column('order', 'price')
    op.drop_column('order', 'payment_id')
    op.drop_column('order', 'currency')
    op.drop_table('payment')
