from unittest.mock import patch
import pytest


@pytest.fixture
def mock_payssion(app):
    with patch('pd.ext.payssion.client') as m:
        yield m


@pytest.fixture
def mock_payssion_payment_request(mock_payssion):
    mock_payssion.payment_request.return_value = {
        "todo": "redirect",
        "redirect_url": "https:\/\/www.payssion.com.com\/E806897643289185",
        "transaction": {
                "transaction_id": "E806897643289185",
                "state": "pending",
                "amount": "10.00",
                "currency": "USD",
                "order_id": ""
        },
        "result_code": 200
    }
    return mock_payssion.payment_request


@pytest.fixture
def mock_payssion_payment_details(mock_payssion):
    mock_payssion.payment_details.return_value = {
        "transaction": {
            "transaction_id": "E806897643289185",
            "state": "pending",
            "amount": "10.00",
            "currency": "USD",
            "order_id": "123",
            "pm_id": "alipay_cn",
            "created": 1493275361,
            "updated": 1493275361,
        },
        "result_code": 200
    }
    return mock_payssion.payment_details


@pytest.fixture
def mock_payssion_notify_signature(mock_payssion):
    # there's no point in validating this signature
    # we just assume it's ok
    mock_payssion.verify_notify_signature.return_value = True
    return mock_payssion.verify_notify_signature


@pytest.fixture
def mock_signals():
    with patch('pd.payment.payssion.api.signals') as m:
        yield m
