from decimal import Decimal
from pd.payment.models import PaymentStatus, Vendors
from pd.statsd import count_payment, count_revenue
from unittest.mock import Mock


def test_payment_handlers():
    payment = Mock(
        vendor=Vendors.payssion,
        status=PaymentStatus.success,
        amount=Decimal('10')
    )
    count_payment(payment)
    count_revenue(payment)
