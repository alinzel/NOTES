"""add post.media_type

Revision ID: f258e2610401
Revises: 0fc34154b37c
Create Date: 2017-06-08 14:39:52.826367

"""
from unittest.mock import Mock
from alembic import context, op
import sqlalchemy as sa
from pd.facebook.models import Post


# revision identifiers, used by Alembic.
revision = 'f258e2610401'
down_revision = '0fc34154b37c'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'post', sa.Column('media_type', sa.SmallInteger(), nullable=True))
    if not context.is_offline_mode():
        conn = op.get_bind()
        rows = conn.execute('''
        SELECT s.post_id, s.url
        FROM (
          SELECT post_id, url,
            row_number() OVER (PARTITION BY post_id ORDER BY id) AS r
          FROM post_photo
        ) as s
        WHERE s.r = 1
        ''').fetchall()
        if rows:
            values = []
            post = Mock()
            for post_id, url in rows:
                post.photos = [Mock(url=url)]
                values.append((Post.caculate_media_type(post).value, post_id))
            conn.execute('UPDATE post SET media_type=%s WHERE id=%s', *values)


def downgrade():
    op.drop_column('post', 'media_type')
