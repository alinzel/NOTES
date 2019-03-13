from sqlalchemy_utils import CurrencyType
from pd.sqla import db


class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    logo_url = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return 'vendor[{}]'.format(self.name)


class VendorLink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Float, nullable=False)
    currency = db.Column(CurrencyType, nullable=False)
    url = db.Column(db.Text, nullable=False)
    vendor_id = db.Column(
        db.Integer, db.ForeignKey('vendor.id', ondelete='CASCADE'),
        nullable=False,
    )
    vendor = db.relationship(
        'Vendor',
        backref=db.backref(
            'links', cascade='all, delete-orphan', passive_deletes=True
        )
    )
    post_id = db.Column(
        db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'),
        nullable=False,
    )
    post = db.relationship(
        'Post', backref=db.backref(
            'vendor_links', cascade='all, delete-orphan', passive_deletes=True
        )
    )

    def __repr__(self):
        return '[{}]{}{}'.format(
            self.vendor.name, self.price, self.currency.code)
