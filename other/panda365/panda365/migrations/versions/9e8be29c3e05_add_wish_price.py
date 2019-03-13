"""add wish_price

Revision ID: 9e8be29c3e05
Revises: f37637c1bcf8
Create Date: 2017-06-23 11:48:30.684098

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy_utils import CurrencyType

# revision identifiers, used by Alembic.
revision = '9e8be29c3e05'
down_revision = 'f37637c1bcf8'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'wish_price',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('country', sa.Text(), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('currency', CurrencyType(length=3), nullable=False),
        sa.Column('wish_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['wish_id'], ['wish.id'], name=op.f(
            'fk_wish_price_wish_id_wish'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_wish_price'))
    )
    op.drop_column('wish', 'price')
    op.drop_column('wish', 'currency')


def downgrade():
    op.add_column(
        'wish', sa.Column('currency', CurrencyType(length=3), nullable=True))
    op.add_column('wish', sa.Column('price', sa.Float(), nullable=True))
    op.drop_table('wish_price')
