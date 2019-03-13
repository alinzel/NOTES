"""inactivate fb posts

Revision ID: f37637c1bcf8
Revises: 43c7ecf8ed02
Create Date: 2017-06-22 12:01:59.623040

"""
from alembic import op
from pd.facebook.models import MediaType


# revision identifiers, used by Alembic.
revision = 'f37637c1bcf8'
down_revision = '43c7ecf8ed02'
branch_labels = None
depends_on = None

# set active status of posts
update = "UPDATE post SET is_active = {}"
# filter those: not gif, and not shopping; 3 == gif
where = "WHERE media_type != {} AND is_shopping = false".format(
    MediaType.gif.value)


def upgrade():
    op.execute(' '.join([update.format('false'), where]))


def downgrade():
    op.execute(' '.join([update.format('true'), where]))
