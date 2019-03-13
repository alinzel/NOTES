"""uq_like_user_parent

Revision ID: 9ecf7526c788
Revises: e2f3d212f4c8
Create Date: 2017-04-19 14:39:15.254838

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '9ecf7526c788'
down_revision = 'e2f3d212f4c8'
branch_labels = None
depends_on = None


def upgrade():
    op.create_unique_constraint(
        'uq_like_user_parent', 'like',
        ['user_id', 'parent_id', 'parent_type'])


def downgrade():
    op.drop_constraint('uq_like_user_parent', 'like', type_='unique')
