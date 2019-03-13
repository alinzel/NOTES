"""ondelete cascade post_photo.post_id

Revision ID: e2f3d212f4c8
Revises: d24f9f5ccca8
Create Date: 2017-04-19 11:21:05.955332

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'e2f3d212f4c8'
down_revision = 'd24f9f5ccca8'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint(
        'fk_post_photo_post_id_post', 'post_photo', type_='foreignkey')
    op.create_foreign_key(
        op.f('fk_post_photo_post_id_post'), 'post_photo', 'post',
        ['post_id'], ['id'], ondelete='CASCADE')


def downgrade():
    op.drop_constraint(
        op.f('fk_post_photo_post_id_post'), 'post_photo', type_='foreignkey')
    op.create_foreign_key(
        'fk_post_photo_post_id_post', 'post_photo', 'post',
        ['post_id'], ['id'])
