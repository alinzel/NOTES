"""add likes_num and comments_num

Revision ID: 11a6c0641820
Revises: 6c28338a61c2
Create Date: 2017-04-14 14:22:36.092490

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '11a6c0641820'
down_revision = '6c28338a61c2'
branch_labels = None
depends_on = None


def upgrade():
    # comment
    op.add_column(
        'comment', sa.Column(
            'comments_num', sa.Integer(), server_default='0', nullable=True))
    op.add_column(
        'comment', sa.Column(
            'likes_num', sa.Integer(), server_default='0', nullable=True))
    op.add_column(
        'comment', sa.Column('parent_id', sa.Integer(), nullable=True))
    op.add_column(
        'comment', sa.Column('parent_type', sa.Text(), nullable=True))
    op.execute(
        "UPDATE comment SET parent_id = post_id, parent_type = 'Post'"
    )
    op.alter_column('comment', 'parent_id', nullable=False)
    op.alter_column('comment', 'parent_type', nullable=False)

    op.drop_constraint(
        'fk_comment_user_id_user', 'comment', type_='foreignkey')
    op.drop_constraint(
        'fk_comment_parent_comment_id_comment', 'comment', type_='foreignkey')
    op.drop_constraint(
        'fk_comment_post_id_post', 'comment', type_='foreignkey')
    op.create_foreign_key(
        op.f('fk_comment_user_id_user'), 'comment', 'user',
        ['user_id'], ['id'], ondelete='CASCADE')
    op.drop_column('comment', 'parent_comment_id')
    op.drop_column('comment', 'post_id')
    # like
    op.add_column('like', sa.Column('parent_id', sa.Integer(), nullable=False))
    op.add_column('like', sa.Column('parent_type', sa.Text(), nullable=False))
    op.drop_constraint('fk_like_user_id_user', 'like', type_='foreignkey')
    op.create_foreign_key(
        op.f('fk_like_user_id_user'), 'like', 'user',
        ['user_id'], ['id'], ondelete='CASCADE')
    op.drop_column('like', 'target_id')
    op.drop_column('like', 'target_type')
    op.drop_constraint('fk_post_user_id_user', 'post', type_='foreignkey')
    op.create_foreign_key(
        op.f('fk_post_user_id_user'), 'post', 'user',
        ['user_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint(
        'fk_post_photo_user_id_user', 'post_photo', type_='foreignkey')
    op.create_foreign_key(
        op.f('fk_post_photo_user_id_user'), 'post_photo', 'user',
        ['user_id'], ['id'], ondelete='CASCADE')
    # post
    op.alter_column('post', 'comments_num', server_default='0')
    op.alter_column('post', 'likes_num', server_default='0')


def downgrade():
    op.drop_constraint(
        op.f('fk_post_photo_user_id_user'), 'post_photo', type_='foreignkey')
    op.create_foreign_key(
        'fk_post_photo_user_id_user', 'post_photo', 'user',
        ['user_id'], ['id'])
    op.drop_constraint(
        op.f('fk_post_user_id_user'), 'post', type_='foreignkey')
    op.create_foreign_key(
        'fk_post_user_id_user', 'post', 'user', ['user_id'], ['id'])
    op.add_column(
        'like', sa.Column(
            'target_type', sa.TEXT(), autoincrement=False, nullable=False))
    op.add_column(
        'like', sa.Column(
            'target_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(op.f('fk_like_user_id_user'),
                       'like', type_='foreignkey')
    op.create_foreign_key(
        'fk_like_user_id_user', 'like', 'user', ['user_id'], ['id'])
    op.drop_column('like', 'parent_type')
    op.drop_column('like', 'parent_id')
    op.add_column(
        'comment', sa.Column(
            'post_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column(
        'comment', sa.Column(
            'parent_comment_id', sa.INTEGER(), autoincrement=False,
            nullable=True))
    op.drop_constraint(
        op.f('fk_comment_user_id_user'), 'comment', type_='foreignkey')
    op.create_foreign_key(
        'fk_comment_post_id_post', 'comment', 'post',
        ['post_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(
        'fk_comment_parent_comment_id_comment', 'comment', 'comment',
        ['parent_comment_id'], ['id'])
    op.create_foreign_key(
        'fk_comment_user_id_user', 'comment', 'user', ['user_id'], ['id'])
    op.drop_column('comment', 'parent_type')
    op.drop_column('comment', 'parent_id')
    op.drop_column('comment', 'likes_num')
    op.drop_column('comment', 'comments_num')
    # post
    op.alter_column('post', 'comments_num', server_default=None)
    op.alter_column('post', 'likes_num', server_default=None)
