"""add product_info

Revision ID: c335985ef89b
Revises: 9e8be29c3e05
Create Date: 2017-06-26 17:07:16.269833

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c335985ef89b'
down_revision = '9e8be29c3e05'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'post',
        sa.Column(
            'info_translations', postgresql.JSONB(astext_type=sa.Text()),
            nullable=True
        )
    )
    op.add_column(
        'wish',
        sa.Column(
            'info_translations', postgresql.JSONB(astext_type=sa.Text()),
            nullable=True
        )
    )


def downgrade():
    op.drop_column('wish', 'info_translations')
    op.drop_column('post', 'info_translations')
