"""add conf

Revision ID: d24f9f5ccca8
Revises: 11a6c0641820
Create Date: 2017-04-18 15:30:27.602687

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd24f9f5ccca8'
down_revision = '11a6c0641820'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'conf',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('version', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_conf')),
        sa.UniqueConstraint('name', name=op.f('uq_conf_name'))
    )


def downgrade():
    op.drop_table('conf')
