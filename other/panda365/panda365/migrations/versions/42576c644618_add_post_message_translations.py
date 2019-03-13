"""replace post.message with message_translations

Revision ID: 42576c644618
Revises: 1f74ea45e765
Create Date: 2017-05-03 15:18:39.655720

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '42576c644618'
down_revision = '1f74ea45e765'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'post',
        sa.Column(
            'message_translations',
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True))
    # data migration
    op.execute(
        "UPDATE post SET message_translations = jsonb_build_object('en', message)"  # noqa
    )
    op.drop_column('post', 'message')


def downgrade():
    op.add_column(
        'post',
        sa.Column('message', sa.TEXT(), autoincrement=False, nullable=True))
    op.execute(
        "UPDATE post SET message = message_translations->>'en'"
    )
    op.drop_column('post', 'message_translations')
