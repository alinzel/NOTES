"""add category table

Revision ID: 02467a650300
Revises: 51083daea9cc
Create Date: 2017-07-26 19:57:40.375321

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '02467a650300'
down_revision = '51083daea9cc'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('category',
                    sa.Column(
                        'name_translations',
                        postgresql.JSONB(astext_type=sa.Text()),
                        nullable=True),
                    sa.Column(
                        'id', sa.Integer(), nullable=False),
                    sa.Column(
                        'sort_weight', sa.Float(),
                        server_default='0', nullable=False),
                    sa.PrimaryKeyConstraint('id', name=op.f('pk_category'))
                    )
    op.add_column(
        'batch', sa.Column(
            'category_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        op.f('fk_batch_category_id_category'),
        'batch', 'category', ['category_id'], ['id'])
    op.add_column(
        'game', sa.Column(
            'category_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        op.f('fk_game_category_id_category'),
        'game', 'category', ['category_id'], ['id'])


def downgrade():
    op.drop_constraint(
        op.f('fk_game_category_id_category'), 'game', type_='foreignkey')
    op.drop_column('game', 'category_id')
    op.drop_constraint(
        op.f('fk_batch_category_id_category'), 'batch', type_='foreignkey')
    op.drop_column('batch', 'category_id')
    op.drop_table('category')
