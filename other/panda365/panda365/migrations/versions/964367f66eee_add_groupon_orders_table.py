"""add groupon orders table

Revision ID: 964367f66eee
Revises: 4c169374ba37
Create Date: 2017-07-13 15:22:24.649714

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy_utils import ArrowType


# revision identifiers, used by Alembic.
revision = '964367f66eee'
down_revision = '4c169374ba37'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'order',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', ArrowType(), nullable=True),
        sa.Column('updated_at', ArrowType(), nullable=True),
        sa.Column('full_name', sa.Text(), nullable=False),
        sa.Column('complete_address', sa.Text(), nullable=False),
        sa.Column('postcode', sa.Text(), nullable=False),
        sa.Column('city', sa.Text(), nullable=False),
        sa.Column('province', sa.Text(), nullable=False),
        sa.Column('phone', sa.Text(), nullable=False),
        sa.Column('email', sa.Text(), nullable=False),
        sa.Column('status', sa.SmallInteger(), nullable=True),
        sa.Column('batch_id', sa.Integer(), nullable=False),
        sa.Column('game_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['batch_id'], ['batch.id'], name=op.f('fk_order_batch_id_batch')),
        sa.ForeignKeyConstraint(
            ['game_id'], ['game.id'], name=op.f('fk_order_game_id_game')),
        sa.ForeignKeyConstraint(
            ['user_id'], ['user.id'], name=op.f('fk_order_user_id_user')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_order')),
        sa.UniqueConstraint('game_id', 'user_id', name='uq_order_game_user')
    )
    op.add_column(
        'batch', sa.Column('finish_status', sa.SmallInteger(), nullable=True))
    op.add_column(
        'batch', sa.Column('games_count', sa.Integer(), nullable=True))
    op.add_column('batch', sa.Column('sold_num', sa.Integer(), nullable=True))
    op.add_column('game', sa.Column('issue_id', sa.Integer(), nullable=False))


def downgrade():
    op.drop_column('game', 'issue_id')
    op.drop_column('batch', 'sold_num')
    op.drop_column('batch', 'games_count')
    op.drop_column('batch', 'finish_status')
    op.drop_table('order')
