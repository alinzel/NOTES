"""add post.country

Revision ID: ac873cae540b
Revises: f258e2610401
Create Date: 2017-06-13 13:54:29.162007

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ac873cae540b'
down_revision = 'f258e2610401'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('post', sa.Column('country', sa.Text(), nullable=True))
    # set country of all existing products as MY
    op.execute('''UPDATE post SET country = 'MY' WHERE is_shopping = true''')


def downgrade():
    op.drop_column('post', 'country')
