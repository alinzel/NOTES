"""add user token expire_at

Revision ID: 6c28338a61c2
Revises: 387edd6b9fb1
Create Date: 2017-04-06 10:46:03.947760

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy_utils import ArrowType


# revision identifiers, used by Alembic.
revision = '6c28338a61c2'
down_revision = '387edd6b9fb1'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'user',
        sa.Column('access_token_expire_at', ArrowType(), nullable=True))


def downgrade():
    op.drop_column('user', 'access_token_expire_at')
