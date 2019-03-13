"""add bookmark

Revision ID: 1b3142c54dd6
Revises: e29b804d6d33
Create Date: 2017-05-16 15:37:30.677077

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy_utils import ArrowType


# revision identifiers, used by Alembic.
revision = '1b3142c54dd6'
down_revision = 'e29b804d6d33'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'bookmark',
        sa.Column('created_at', ArrowType(), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('post_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['post_id'], ['post.id'], name=op.f(
            'fk_bookmark_post_id_post'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], name=op.f(
            'fk_bookmark_user_id_user'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_bookmark')),
        sa.UniqueConstraint('user_id', 'post_id',
                            name='uq_bookmark_user_id_post_id')
    )
    op.create_index(
        op.f('ix_bookmark_user_id'), 'bookmark', ['user_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_bookmark_user_id'), table_name='bookmark')
    op.drop_table('bookmark')
