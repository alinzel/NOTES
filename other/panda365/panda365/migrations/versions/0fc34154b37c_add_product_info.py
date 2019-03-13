"""add product_info

Revision ID: 0fc34154b37c
Revises: a204c018cd94
Create Date: 2017-06-06 16:28:57.290383

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy_utils import ArrowType, CurrencyType


# revision identifiers, used by Alembic.
revision = '0fc34154b37c'
down_revision = 'a204c018cd94'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('post', sa.Column(
        'currency', CurrencyType(length=3), nullable=True))
    op.add_column('post', sa.Column('price', sa.Float(), nullable=True))
    op.add_column('post', sa.Column('sale_on', sa.Date(), nullable=True))
    op.add_column('post', sa.Column('updated_at', ArrowType(), nullable=True))
    op.execute('UPDATE post SET updated_at = created_at')


def downgrade():
    op.drop_column('post', 'updated_at')
    op.drop_column('post', 'sale_on')
    op.drop_column('post', 'price')
    op.drop_column('post', 'currency')
