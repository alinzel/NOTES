"""add post related models

Revision ID: 387edd6b9fb1
Revises: 8ed9a78599fc
Create Date: 2017-03-22 16:56:55.490010

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy_utils import ArrowType


# revision identifiers, used by Alembic.
revision = '387edd6b9fb1'
down_revision = '8ed9a78599fc'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', ArrowType(), nullable=True),
        sa.Column('fb_id', sa.Text(), nullable=True),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('icon', sa.Text(), nullable=True),
        sa.Column('access_token', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_user')),
        sa.UniqueConstraint('fb_id', name=op.f('uq_user_fb_id'))
    )
    op.create_table(
        'like',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', ArrowType(), nullable=True),
        sa.Column('fb_id', sa.Text(), nullable=True),
        sa.Column('target_id', sa.Integer(), nullable=False),
        sa.Column('target_type', sa.Text(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ['user_id'], ['user.id'], name=op.f('fk_like_user_id_user')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_like')),
        sa.UniqueConstraint('fb_id', name=op.f('uq_like_fb_id'))
    )
    op.create_table(
        'post',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', ArrowType(), nullable=True),
        sa.Column('fb_id', sa.Text(), nullable=True),
        sa.Column('fb_page_id', sa.Text(), nullable=False),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('comments_num', sa.Integer(), nullable=True),
        sa.Column('likes_num', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ['user_id'], ['user.id'], name=op.f('fk_post_user_id_user')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_post')),
        sa.UniqueConstraint('fb_id', name=op.f('uq_post_fb_id'))
    )
    op.create_table(
        'comment',
        sa.Column('created_at', ArrowType(), nullable=True),
        sa.Column('fb_id', sa.Text(), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('photo_url', sa.Text(), nullable=True),
        sa.Column('parent_comment_id', sa.Integer(), nullable=True),
        sa.Column('post_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ['parent_comment_id'], ['comment.id'],
            name=op.f('fk_comment_parent_comment_id_comment')),
        sa.ForeignKeyConstraint(['post_id'], ['post.id'], name=op.f(
            'fk_comment_post_id_post'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(
            ['user_id'], ['user.id'], name=op.f('fk_comment_user_id_user')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_comment')),
        sa.UniqueConstraint('fb_id', name=op.f('uq_comment_fb_id'))
    )
    op.create_table(
        'post_photo',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('url', sa.Text(), nullable=False),
        sa.Column('post_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['post_id'], ['post.id'], name=op.f(
            'fk_post_photo_post_id_post')),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], name=op.f(
            'fk_post_photo_user_id_user')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_post_photo'))
    )


def downgrade():
    op.drop_table('post_photo')
    op.drop_table('comment')
    op.drop_table('post')
    op.drop_table('like')
    op.drop_table('user')
