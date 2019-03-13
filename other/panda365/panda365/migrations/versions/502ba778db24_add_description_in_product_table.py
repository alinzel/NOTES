"""add description in product table

Revision ID: 502ba778db24
Revises: e16e7cf6bf97
Create Date: 2017-08-08 15:02:31.578666

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '502ba778db24'
down_revision = 'e16e7cf6bf97'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'product', sa.Column(
            'description_translations',
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True
        )
    )


def downgrade():
    op.drop_column('product', 'description_translations')
