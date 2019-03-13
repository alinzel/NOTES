from enum import Enum
from furl import furl
from pd.sqla import db, TimestampMixin
from sqlalchemy.dialects.postgresql import JSONB
from uuid import uuid4
import sqlalchemy_utils as su


class PaymentStatus(Enum):
    pending = 1
    success = 2
    canceled = 3
    error = 4
    failed = 5
    expired = 6


class Vendors(Enum):
    payssion = 1


class Payment(TimestampMixin, db.Model):
    method = db.Column(db.Text)
    amount = db.Column(db.DECIMAL, nullable=False)
    currency = db.Column(su.CurrencyType, nullable=False)
    status = db.Column(
        su.ChoiceType(PaymentStatus, impl=db.SmallInteger()),
        default=PaymentStatus.pending,
    )
    vendor = db.Column(
        su.ChoiceType(Vendors, impl=db.SmallInteger()),
        nullable=False,
    )
    transaction_id = db.Column(db.Text, doc='第三方支付id')
    ref_id = db.Column(
        db.Text, default=lambda: uuid4().hex, doc='在第三方系统中我方的引用id')

    # 支付对象
    object_type = db.Column(db.Text, nullable=False)
    object_id = db.Column(db.Integer, nullable=False)
    object = su.generic_relationship(object_type, object_id)

    order = db.relationship(
        'Order', doc='团购订单',
        primaryjoin=(
            "and_(Payment.object_id == foreign(Order.id), "
            "Payment.object_type == 'Order')"
        ),
        uselist=False,
    )

    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id'), nullable=False,
    )
    user = db.relationship('User', backref='payments')

    extra_data = db.Column(JSONB)
    return_url = db.Column(db.Text)

    @property
    def redirect_url(self):
        url = furl(self.return_url)
        url.args['status'] = self.status.name
        return url.url

    @property
    def payment_url(self):
        if self.vendor == Vendors.payssion:
            if self.extra_data and 'redirect_url' in self.extra_data:
                return self.extra_data['redirect_url']
        else:  # pragma: no cover
            return None

    def __repr__(self):
        return '[{vendor}]{amount} {currency}'.format(
            vendor=self.vendor.name,
            amount=self.amount,
            currency=self.currency,
        )
