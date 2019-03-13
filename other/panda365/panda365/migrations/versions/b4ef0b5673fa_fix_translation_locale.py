"""fix translation locale

Revision ID: b4ef0b5673fa
Revises: 9e8be29c3e05
Create Date: 2017-06-27 15:17:47.738087

Locale of Malaysia should have been "ms" instead of "my". Due to errors in
configuration, message_translations are storing "my" as key. This causes
clients sending "Accept-Language: ms" getting English version of messages.

This migration copy the contents of "my" to "ms".
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'b4ef0b5673fa'
down_revision = '9e8be29c3e05'
branch_labels = None
depends_on = None


def upgrade():
    for table in ('post', 'wish'):
        # what we're doing here:
        # set message_translations['ms'] to message_translations['my']
        # delete message_translations['my']
        # apply only to rows containing key "my"
        op.execute('''
            UPDATE {} SET message_translations = (
              (message_translations ||
                jsonb_build_object('ms', message_translations->>'my')) - 'my'
            )
            WHERE message_translations ? 'my'
        '''.format(table))


def downgrade():
    for table in ('post', 'wish'):
        op.execute('''
            UPDATE {} SET message_translations = (
              (message_translations ||
                jsonb_build_object('my', message_translations->>'ms')) - 'ms'
            )
            WHERE message_translations ? 'ms'
        '''.format(table))
