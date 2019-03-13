"""add admin user and role table

Revision ID: 8ed9a78599fc
Revises:
Create Date: 2017-03-20 14:38:48.378768

"""
from alembic import op
from flask import current_app
import sqlalchemy as sa
from sqlalchemy_utils import EmailType


# revision identifiers, used by Alembic.
revision = '8ed9a78599fc'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'admin_role',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.Text(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_admin_role')),
        sa.UniqueConstraint('name', name=op.f('uq_admin_role_name'))
    )
    op.create_table(
        'admin_user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', EmailType(length=255), nullable=True),
        sa.Column('password', sa.Text(), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=True),
        sa.Column('confirmed_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_admin_user')),
        sa.UniqueConstraint('email', name=op.f('uq_admin_user_email'))
    )
    op.create_table(
        'admin_roles_users',
        sa.Column('admin_user_id', sa.Integer(), nullable=True),
        sa.Column('admin_role_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ['admin_role_id'], ['admin_role.id'], name=op.f(
                'fk_admin_roles_users_admin_role_id_admin_role')),
        sa.ForeignKeyConstraint(
            ['admin_user_id'], ['admin_user.id'], name=op.f(
                'fk_admin_roles_users_admin_user_id_admin_user'))
    )
    if current_app.config['DEBUG']:
        # create dev role
        op.execute("INSERT INTO admin_role (id, name) VALUES (1, 'dev')")
        # create super user
        op.execute("""
            INSERT INTO admin_user (id, email, password, active, confirmed_at)
            VALUES (1, 'u@dev.com', '$2b$12$FFa5Z0972YS/N.0uQ5gXuuamCEFBgEjPUwT5SpfO5B6zXtR20rKQa', true, '2017-01-01 00:00:00')"""  # noqa
        )
        op.execute("INSERT INTO admin_roles_users VALUES (1, 1)")


def downgrade():
    op.drop_table('admin_roles_users')
    op.drop_table('admin_user')
    op.drop_table('admin_role')
