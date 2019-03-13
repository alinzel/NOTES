from pd.payment.factory import PaymentFactory
from pd.payment.models import PaymentStatus


def test_payment():
    p = PaymentFactory.build()
    assert p.status == PaymentStatus.pending
    assert p.user
    assert p.payment_url
    p.extra_data = {}
    assert not p.payment_url
    p.extra_data = None
    assert not p.payment_url
