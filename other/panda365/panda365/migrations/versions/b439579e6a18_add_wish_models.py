"""add wish models

Revision ID: b439579e6a18
Revises: ac873cae540b
Create Date: 2017-06-19 18:33:46.930643

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy_utils import ArrowType
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'b439579e6a18'
down_revision = 'ac873cae540b'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'tip',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('message_translations', postgresql.JSONB(
            astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_tip'))
    )
    op.create_table(
        'wish',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', ArrowType(), nullable=True),
        sa.Column('updated_at', ArrowType(), nullable=True),
        sa.Column('status', sa.SmallInteger(), nullable=False),
        sa.Column('message_translations', postgresql.JSONB(
            astext_type=sa.Text()), nullable=True),
        sa.Column('votes_target', sa.Integer(), nullable=False),
        sa.Column('tip_id', sa.Integer(), nullable=False),
        sa.Column('votes_num', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['tip_id'], ['tip.id'],
                                name=op.f('fk_wish_tip_id_tip')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_wish'))
    )
    op.create_table(
        'vote',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('wish_id', sa.Integer(), nullable=False),
        sa.Column('created_at', ArrowType(), nullable=True),
        sa.Column('created_date', sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], name=op.f(
            'fk_vote_user_id_user'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['wish_id'], ['wish.id'], name=op.f(
            'fk_vote_wish_id_wish'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_vote')),
        sa.UniqueConstraint('user_id', 'wish_id',
                            'created_date', name='uq_vote_daily_per_user')
    )
    op.create_table(
        'wish_media',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('url', sa.Text(), nullable=False),
        sa.Column('wish_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['wish_id'], ['wish.id'], name=op.f(
            'fk_wish_media_wish_id_wish'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_wish_media'))
    )


def downgrade():
    op.drop_table('wish_media')
    op.drop_table('vote')
    op.drop_table('wish')
    op.drop_table('tip')
