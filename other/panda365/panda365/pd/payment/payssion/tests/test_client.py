import hashlib
from unittest.mock import Mock, patch

import pytest

from pd.payment.payssion.client import (
    Client, APIError, PaymentRequestError
)


@pytest.fixture
def client():
    c = Client('key', 'secret')
    c.request = Mock()
    c.request.return_value.status_code = 200
    c.request.return_value.json.return_value = {
        'result_code': 200
    }
    return c


def test_signature():
    client = Client('key', 'secret')
    assert client._get_signature('a', '1') == hashlib.md5('|'.join([
        client.api_key, 'a', '1', client.api_secret,
    ]).encode()).hexdigest()
    # should convert to string automatically
    assert client._get_signature('a', 1.1) == client._get_signature('a', '1.1')


@pytest.mark.parametrize('sandbox,expected_url', [
    [False, 'https://www.payssion.com/api/v1/payment/create'],
    [True, 'http://sandbox.payssion.com/api/v1/payment/create']
])
def test_request_url(sandbox, expected_url):
    client = Client('key', 'secret', sandbox)
    with patch('requests.Session.request') as mock_request:
        client.get('/payment/create')
        assert mock_request.called
        args, kwargs = mock_request.call_args
        assert args[1] == expected_url


def _get_payment_request_data(**kwargs):
    default = {
        'amount': 10.23,
        'currency': 'USD',
        'pm_id': 'cashu',
        'description': '123',
        'order_id': 'oid',
        'return_url': 'http://example.com',
    }
    default.update(kwargs)
    return default


def test_payment_request(client):
    ret = client.request.return_value.json.return_value
    ret['result_code'] = 400
    with pytest.raises(PaymentRequestError):
        client.payment_request(**_get_payment_request_data())

    ret['result_code'] = 200
    assert client.payment_request(**_get_payment_request_data())
    assert client.payment_request(**_get_payment_request_data(return_url=None))

    client.request.return_value.status_code = 500
    with pytest.raises(APIError):
        client.payment_request(**_get_payment_request_data())


def test_payment_details(client):

    ret = client.request.return_value.json.return_value
    for status, expect_data in (
        [200, True],
        [404, False],
    ):
        ret['result_code'] = status
        assert bool(
            client.payment_details('E806897643289185', '123')) == expect_data

    ret['result_code'] = 503  # unexpected status code
    with pytest.raises(APIError):
        client.payment_details('E806897643289185', '123')


def test_payment_details_unexpected_error(client):
    resp = client.request.return_value
    resp.status_code = 500
    with pytest.raises(APIError):
        client.payment_details('E806897643289185', '123')
    assert not resp.json.called


@pytest.mark.parametrize('sig,expect_ok', [
    ['invalid', False],
    ['2773d5e44a2c5f81bf60ef59d01e344c', True],
])
def test_verify_notification_signature(client, sig, expect_ok):
    # pm_id, amount, currency, order_id, state
    client.api_key = 'api_key'
    client.api_secret = 'api_secret'
    kwargs = dict(
        pm_id='alipay_cn',
        amount='1.00',
        currency='USD',
        order_id='566a22452ede455cb351737553935121',
        state='pending',
        signature=sig,
    )
    assert client.verify_notify_signature(**kwargs) == expect_ok
