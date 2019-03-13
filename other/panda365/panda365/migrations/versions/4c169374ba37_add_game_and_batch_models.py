"""add game and batch models

Revision ID: 4c169374ba37
Revises: b3e94bb280df
Create Date: 2017-07-10 18:10:41.585069

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy_utils import ArrowType, CurrencyType

# revision identifiers, used by Alembic.
revision = '4c169374ba37'
down_revision = 'b3e94bb280df'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'spec',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name_translations', postgresql.JSONB(
            astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_spec'))
    )
    op.create_table(
        'spec_option',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('value_translations', postgresql.JSONB(
            astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_spec_option'))
    )
    op.create_table(
        'batch',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at',
                  ArrowType(), nullable=True),
        sa.Column(
            'country', sa.Text, nullable=False),
        sa.Column('price', sa.DECIMAL(), nullable=False),
        sa.Column('currency', CurrencyType(
            length=3), nullable=False),
        sa.Column('market_price', sa.DECIMAL(), nullable=False),
        sa.Column('market_currency', CurrencyType(
            length=3), nullable=False),
        sa.Column('shipping_price', sa.DECIMAL(), nullable=False),
        sa.Column('shipping_currency', CurrencyType(
            length=3), nullable=False),
        sa.Column('total_shares', sa.Integer(), nullable=False),
        sa.Column(
            'start_at', ArrowType(), nullable=False),
        sa.Column('end_at', ArrowType(),
                  nullable=False),
        sa.Column('direct_buy_url', sa.Text(), nullable=True),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['product.id'], name=op.f(
            'fk_batch_product_id_product')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_batch'))
    )
    op.create_table(
        'batch_spec',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('batch_id', sa.Integer(), nullable=False),
        sa.Column('spec_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['batch_id'], ['batch.id'], name=op.f(
            'fk_batch_spec_batch_id_batch')),
        sa.ForeignKeyConstraint(['spec_id'], ['spec.id'], name=op.f(
            'fk_batch_spec_spec_id_spec')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_batch_spec'))
    )
    op.create_table(
        'game',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column(
            'created_at', ArrowType(), nullable=True),
        sa.Column(
            'country', sa.Text, nullable=False),
        sa.Column('price', sa.DECIMAL(), nullable=False),
        sa.Column('currency', CurrencyType(
            length=3), nullable=False),
        sa.Column('market_price', sa.DECIMAL(), nullable=False),
        sa.Column('market_currency', CurrencyType(
            length=3), nullable=False),
        sa.Column('shipping_price', sa.DECIMAL(), nullable=False),
        sa.Column('shipping_currency', CurrencyType(
            length=3), nullable=False),
        sa.Column('total_shares', sa.Integer(), nullable=False),
        sa.Column(
            'start_at', ArrowType(), nullable=False),
        sa.Column('end_at', ArrowType(),
                  nullable=False),
        sa.Column('direct_buy_url', sa.Text(), nullable=True),
        sa.Column('batch_id', sa.Integer(), nullable=False),
        sa.Column('left_shares', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.CheckConstraint('left_shares >= 0', name=op.f(
            'ck_game_left_shares_gte_0')),
        sa.ForeignKeyConstraint(
            ['batch_id'], ['batch.id'], name=op.f('fk_game_batch_id_batch')),
        sa.ForeignKeyConstraint(['product_id'], ['product.id'], name=op.f(
            'fk_game_product_id_product')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_game'))
    )
    op.create_table(
        'batch_spec_options',
        sa.Column('batch_spec_id', sa.Integer(), nullable=True),
        sa.Column('spec_option_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ['batch_spec_id'], ['batch_spec.id'], name=op.f(
                'fk_batch_spec_options_batch_spec_id_batch_spec')),
        sa.ForeignKeyConstraint(
            ['spec_option_id'], ['spec_option.id'], name=op.f(
                'fk_batch_spec_options_spec_option_id_spec_option'))
    )


def downgrade():
    op.drop_table('batch_spec_options')
    op.drop_table('game')
    op.drop_table('batch_spec')
    op.drop_table('batch')
    op.drop_table('spec_option')
    op.drop_table('spec')
