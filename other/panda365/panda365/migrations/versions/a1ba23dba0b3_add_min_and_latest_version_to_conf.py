"""add min and latest version to conf

Revision ID: a1ba23dba0b3
Revises: dbf55d071d34
Create Date: 2017-07-06 11:28:53.482211

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1ba23dba0b3'
down_revision = 'dbf55d071d34'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('conf', sa.Column('description', sa.Text(), nullable=True))
    op.add_column(
        'conf', sa.Column('latest_version', sa.Integer(), nullable=False))
    op.add_column(
        'conf', sa.Column('min_version', sa.Integer(), nullable=False))
    op.drop_column('conf', 'version')


def downgrade():
    op.add_column(
        'conf',
        sa.Column('version', sa.TEXT(), autoincrement=False, nullable=True))
    op.drop_column('conf', 'min_version')
    op.drop_column('conf', 'latest_version')
    op.drop_column('conf', 'description')
