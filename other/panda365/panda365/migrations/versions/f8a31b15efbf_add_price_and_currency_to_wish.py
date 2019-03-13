"""add price and currency to wish

Revision ID: f8a31b15efbf
Revises: a0e861911449
Create Date: 2017-06-20 15:52:39.945397

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy_utils import CurrencyType


# revision identifiers, used by Alembic.
revision = 'f8a31b15efbf'
down_revision = 'a0e861911449'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('wish', sa.Column(
        'currency', CurrencyType(length=3), nullable=True))
    op.add_column('wish', sa.Column('price', sa.Float(), nullable=True))


def downgrade():
    op.drop_column('wish', 'price')
    op.drop_column('wish', 'currency')
