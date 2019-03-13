"""fix action num

Revision ID: a204c018cd94
Revises: 1b3142c54dd6
Create Date: 2017-06-02 10:43:56.224771

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'a204c018cd94'
down_revision = '1b3142c54dd6'
branch_labels = None
depends_on = None


def upgrade():
    for child_table, parent_type, parent_table, num_col in (
        ('comment', 'Post', 'post', 'comments_num'),
        ('"like"', 'Post', 'post', 'likes_num'),
        ('comment', 'Comment', 'comment', 'comments_num'),
        ('"like"', 'Comment', 'comment', 'likes_num'),
    ):
        op.execute('''
        WITH new_values AS (
            SELECT parent_id, count(id)
            FROM {child_table}
            WHERE parent_type = '{parent_type}'
            GROUP BY parent_id
        )
        UPDATE {parent_table}
        SET {num_col} = new_values.count
        FROM new_values
        WHERE id = new_values.parent_id
        '''.format(
            child_table=child_table,
            parent_table=parent_table,
            parent_type=parent_type,
            num_col=num_col,
        ))


def downgrade():
    pass
