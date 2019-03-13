import pytest

from pd.payment.models import PaymentStatus
from pd.payment.payssion.client import PaymentStatus as PayssionPaymentStatus

URL = '/v1/payments/payssion/notify'


@pytest.fixture
def post_data(payment):
    return {
        'pm_id': payment.method,
        'transaction_id': payment.transaction_id,
        'order_id': payment.ref_id,
        'amount': str(payment.amount),
        'currency': str(payment.currency),
        'state': PayssionPaymentStatus.pending.name,
        'notify_sig': 'notify_sig',
    }


def test_notify(
    client, payment, post_data, mock_signals, mock_payssion_notify_signature,
):
    post_data['state'] = PayssionPaymentStatus.completed.name

    for i in range(2):  # should be idempotent for the same input
        resp = client.post(URL, data=post_data)
        assert resp.status_code == 200, resp.json
        assert payment.status == PaymentStatus.success
    assert mock_signals.payment_succeeded.send.call_count == 1


def test_notify_pending(
    client, payment, post_data, mock_payssion_notify_signature,
):
    resp = client.post(URL, data=post_data)
    assert resp.status_code == 200
    assert payment.status == PaymentStatus.pending


def test_notify_no_such_payment(
    client, post_data, payment, mock_payssion_notify_signature,
):
    post_data['order_id'] = '123'
    post_data['state'] = PayssionPaymentStatus.completed.name
    resp = client.post(URL, data=post_data)
    assert resp.status_code == 404


def test_notify_amount_mismatch(
    client, post_data, payment, mock_payssion_notify_signature,
):
    post_data['amount'] = '1000000'
    post_data['state'] = PayssionPaymentStatus.completed.name
    resp = client.post(URL, data=post_data)
    assert resp.status_code == 200  # should ack the notification
    # should mark the status to be error
    assert payment.status == PaymentStatus.error


def test_notify_currency_mismatch(
    client, post_data, payment, mock_signals, mock_payssion_notify_signature
):
    post_data['currency'] = 'MYR'
    post_data['state'] = PayssionPaymentStatus.completed.name
    resp = client.post(URL, data=post_data)
    assert resp.status_code == 200  # should ack the notification
    # should mark the status to be error
    assert payment.status == PaymentStatus.error
    assert mock_signals.payment_error.send.called


def test_invalid_signature(client, post_data):
    resp = client.post(URL, data=post_data)
    assert resp.status_code == 422


def test_invalid_state(client, post_data, mock_payssion_notify_signature):
    post_data['state'] = 'a new state payssion defined but have not told us'
    resp = client.post(URL, data=post_data)
    assert resp.status_code == 422


def test_bad_request(client, post_data, mock_payssion_notify_signature):
    for k in post_data:
        data = dict(post_data)
        data.pop(k)
        resp = client.post(URL, data=data)
        assert resp.status_code == 422
