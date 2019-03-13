from flask_security import UserMixin, RoleMixin
import sqlalchemy_utils as su
from pd.sqla import db

admin_roles_users = db.Table(
    'admin_roles_users',
    db.Column('admin_user_id', db.Integer, db.ForeignKey('admin_user.id')),
    db.Column('admin_role_id', db.Integer, db.ForeignKey('admin_role.id')),
)


class AdminRole(db.Model, RoleMixin):
    name = db.Column(db.Text, unique=True)
    description = db.Column(db.Text)

    def __repr__(self):
        return self.name


class AdminUser(db.Model, UserMixin):
    email = db.Column(su.EmailType, unique=True)
    password = db.Column(db.Text)
    active = db.Column(db.Boolean)
    confirmed_at = db.Column(db.DateTime)
    roles = db.relationship(
        'AdminRole', secondary=admin_roles_users,
        backref=db.backref('users', lazy='dynamic')
    )

    def __repr__(self):
        return '[{}]{}'.format(self.id, self.email)
