"""add product table

Revision ID: b3e94bb280df
Revises: a1ba23dba0b3
Create Date: 2017-07-10 10:37:35.058158

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy_utils import ArrowType

# revision identifiers, used by Alembic.
revision = 'b3e94bb280df'
down_revision = 'a1ba23dba0b3'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'product',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', ArrowType(), nullable=True),
        sa.Column('title_translations', postgresql.JSONB(
            astext_type=sa.Text()), nullable=True),
        sa.Column('info_translations', postgresql.JSONB(
            astext_type=sa.Text()), nullable=True),
        sa.Column('comments_num', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_product'))
    )
    op.create_table(
        'product_media',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('url', sa.Text(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['product.id'], name=op.f(
            'fk_product_media_product_id_product'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_product_media'))
    )


def downgrade():
    op.drop_table('product_media')
    op.drop_table('product')
