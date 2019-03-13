import arrow
import sqlalchemy_utils as su
from sqlalchemy.ext.declarative import declared_attr
from pd.sqla import db
from .base import Base


class User(Base):
    name = db.Column(db.Text, nullable=False)
    icon = db.Column(db.Text)
    access_token = db.Column(db.Text)
    access_token_expire_at = db.Column(su.ArrowType)
    is_bot = db.Column(db.Boolean, default=False, server_default='false')

    def token_expire_soon(self, leeway_seconds=0):
        if not self.access_token_expire_at:
            return True
        ttl = (self.access_token_expire_at - arrow.utcnow()).total_seconds()
        return ttl < leeway_seconds

    @property
    def icon_url(self):
        return (self.icon or
                'https://graph.facebook.com/{}/picture'.format(self.fb_id))

    def __repr__(self):
        return '[{}]{}'.format(self.id, self.name)


class UserCreatedMixin:

    @declared_attr
    def user_id(cls):
        return db.Column(
            db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
