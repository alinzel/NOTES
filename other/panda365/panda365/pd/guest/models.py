from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from pd.sqla import db


class GuestUsers(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    account = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    country = db.Column(db.String(64))

    @property
    def pw(self):
        raise AttributeError('password is not a readable attribute')

    @pw.setter
    def pw(self, password):
        self.password = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password, password)
