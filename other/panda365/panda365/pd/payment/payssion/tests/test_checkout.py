from pd.facebook.factory import UserFactory
from pd.payment.payssion.client import PaymentRequestError
from pd.test_utils import assert_dict_like
import pytest


URL = '/v1/payments/payssion/'


@pytest.fixture
def post_data(order):
    return {
        'method': 'alipay',
        'order_id': order.id,
        'return_url': 'app://payment_return/',
    }


def test_checkout(
        client, mock_payssion_payment_request, post_data, order, batch):
    user = order.user
    client.login(user)

    mock_payssion_payment_request.return_value['amount'] = str(batch.price)

    resp = client.post(URL, data=post_data)
    assert resp.status_code == 200
    # ensure request to payssion is correct
    assert mock_payssion_payment_request.called
    kwargs = mock_payssion_payment_request.call_args[1]
    # amount includes both the price of the item and its shipping fee
    assert kwargs['amount'] == order.amount
    assert kwargs['currency'] == order.currency
    expected_payment_url = (
        mock_payssion_payment_request.return_value['redirect_url'])
    assert_dict_like(resp.json, {
        'method': 'alipay',
        'status': 'pending',
        'amount': float(order.amount),
        'currency': dict(code=order.currency.code),
        'payment_url': expected_payment_url,
    })
    # a payment should be created in db
    assert len(user.payments) == 1
    payment = user.payments[0]
    assert payment.id == resp.json['id']
    assert payment.object is order
    assert payment.order is order


def test_checkout_error(
        client, order, mock_payssion_payment_request, post_data):
    client.login(order.user)

    mock_payssion_payment_request.side_effect = PaymentRequestError(400, 'bad')

    resp = client.post(URL, data=post_data)
    assert resp.status_code == 500
    # no payment should be created
    assert not order.user.payments


@pytest.mark.parametrize('field,error_value', [
    ['method', ''],
    ['order_id', 1234123413241],
])
def test_checkout_params_errors(client, user, post_data, field, error_value):
    client.login(user)
    post_data.update({field: error_value})

    resp = client.post(URL, data=post_data)
    assert resp.status_code == 422
    assert field in resp.json['errors']


def test_checkout_others_order(client, user, order, post_data):
    # there's an order of user in db
    user2 = UserFactory()
    client.login(user2)
    resp = client.post(URL, data=post_data)
    assert resp.status_code == 422
    assert 'cannot be found' in resp.json['errors']['order_id'][0]
