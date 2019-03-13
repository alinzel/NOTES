from furl import furl
from pd.payment.models import PaymentStatus
from pd.payment.payssion.client import APIError
from pd.payment.payssion.client import PaymentStatus as PayssionPaymentStatus
import pytest


URL = '/v1/payments/payssion/return'


@pytest.fixture
def return_args(payment):
    return {
        'order_id': payment.ref_id,
        'transaction_id': payment.transaction_id,
    }


@pytest.fixture
def mock_payssion_payment_details(mock_payssion_payment_details, payment):
    mock_payssion_payment_details.return_value['transaction'].update({
        'transaction_id': payment.transaction_id,
        'amount': str(payment.amount),
        'order_id': payment.ref_id,
        'state': 'completed',
    })
    return mock_payssion_payment_details


def test_callback(
    client, user, return_args, payment, mock_payssion_payment_details,
    mock_signals,
):
    for i in range(2):  # the callback should be idempotent
        resp = client.get(URL, query_string=return_args)

        assert resp.status_code == 302
        location = furl(resp.location)
        assert location.url.startswith(payment.return_url)
        assert location.args['status'] == 'success'
        assert payment.status == PaymentStatus.success
    # should send payment success signal
    assert mock_signals.payment_succeeded.send.call_count == 1
    assert mock_signals.payment_succeeded.send.call_args[0] == (payment,)


def test_payment_not_found(client, return_args):
    return_args['order_id'] = 'fake order id'
    resp = client.get(URL, query_string=return_args)
    assert resp.status_code == 404


def test_payssion_payment_details_error(
        client, mock_payssion_payment_details, return_args, payment):
    # payssion service error
    mock_payssion_payment_details.side_effect = APIError
    resp = client.get(URL, query_string=return_args)

    assert resp.status_code == 500
    assert payment.status == PaymentStatus.pending


def test_payssion_data_corruption(
        client, mock_payssion_payment_details, return_args, payment):
    # payssion data corrupted ;(
    mock_payssion_payment_details.return_value = None
    resp = client.get(URL, query_string=return_args)
    assert resp.status_code == 500
    assert payment.status == PaymentStatus.pending


def test_undefined_payssion_state(
        client, mock_payssion_payment_details, return_args, payment):
    """
    this can happen when payssion adds a state and we haven't update the
    states dict
    """
    mock_payssion_payment_details.return_value[
        'transaction']['state'] = 'some bloody new state'

    resp = client.get(URL, query_string=return_args)

    assert resp.status_code == 422
    # db payment state should remain the same
    assert payment.status == PaymentStatus.pending


@pytest.mark.parametrize('status,expected_status', [
    [PayssionPaymentStatus.error, PaymentStatus.error],
    [PayssionPaymentStatus.failed, PaymentStatus.failed],
    [PayssionPaymentStatus.expired, PaymentStatus.failed],
    [PayssionPaymentStatus.cancelled, PaymentStatus.canceled],
    [PayssionPaymentStatus.cancelled_by_user, PaymentStatus.canceled],
    [PayssionPaymentStatus.pending, PaymentStatus.pending],
    # we don't know how to handle the following states;
    # they are simply ignored and the payment status should remain unchanged
    [PayssionPaymentStatus.awaiting_confirm, PaymentStatus.pending],
    [PayssionPaymentStatus.paid_partial, PaymentStatus.pending],
    [PayssionPaymentStatus.rejected_by_bank, PaymentStatus.pending],
    [PayssionPaymentStatus.refunded, PaymentStatus.pending],
    [PayssionPaymentStatus.refund_pending, PaymentStatus.pending],
    [PayssionPaymentStatus.refund_failed, PaymentStatus.pending],
    [PayssionPaymentStatus.chargeback, PaymentStatus.pending],
])
def test_callback_error_states(
        client, mock_payssion_payment_details, payment, status,
        expected_status, return_args):
    mock_payssion_payment_details.return_value[
        'transaction']['state'] = status.name

    resp = client.get(URL, query_string=return_args)
    assert resp.status_code == 302
    location = furl(resp.location)
    assert location.url.startswith(payment.return_url)
    assert location.args['status'] == expected_status.name
    assert payment.status == expected_status


def test_bad_request(client, payment, return_args):
    for k in return_args:
        q = dict(return_args)
        q.pop(k)
        resp = client.get(URL, query_string=q)
        assert resp.status_code == 422
