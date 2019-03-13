from .models import Payment, PaymentStatus, Vendors
from pd.facebook.factory import UserFactory
from pd.factory import BaseFactory, PositiveDecimal
from sqlalchemy_utils import Currency
import factory


class PaymentFactory(BaseFactory):

    class Meta:
        model = Payment

    amount = PositiveDecimal()
    currency = Currency('USD')
    vendor = factory.Iterator(Vendors)
    transaction_id = factory.Faker('uuid4')
    ref_id = factory.Faker('uuid4')
    user = factory.SubFactory(UserFactory)
    return_url = factory.Faker('url')
    method = 'payment method'
    status = PaymentStatus.pending
    extra_data = factory.LazyAttribute(lambda o: {
        'todo': 'redirect',
        'redirect_url': 'https://www.payssion.com/pay/H722947035681772',
        'transaction': {
            'transaction_id': o.transaction_id,
            'state': o.status.name,
            'amount': float(o.amount),
            'currency': o.currency.code,
            'pm_id': o.method,
            'pm_name': 'Alipay',
            'order_id': o.ref_id
        },
        'result_code': 200
    })
