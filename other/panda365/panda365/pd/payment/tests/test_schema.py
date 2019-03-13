from marshmallow import ValidationError
from pd.groupon.models import OrderStatus
from pd.payment.schema import CheckoutSchema
from unittest.mock import patch
import pytest


def test_checkout_schema(game, order, user):
    schema = CheckoutSchema()

    # other people's order
    data = dict(order_id=order.id, return_url='xxx')
    with patch('pd.payment.schema.current_user_data') as current_user_data:
        current_user_data.__getitem__.return_value = user.id + 1000
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
    exc_info.match('Order.*cannot be found')

    # order status
    order.status = OrderStatus.paid
    data = dict(order_id=order.id, return_url='xxx')
    with patch('pd.payment.schema.current_user_data') as current_user_data:
        current_user_data.__getitem__.return_value = user.id
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
    exc_info.match('is not payment_pending')
