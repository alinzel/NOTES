from enum import Enum
import hashlib
import hmac
import requests


class PaymentStatus(Enum):
    error = 0
    pending = 1
    completed = 2
    paid_partial = 3
    awaiting_confirm = 4
    failed = 5
    cancelled = 6
    cancelled_by_user = 7
    rejected_by_bank = 8
    expired = 9
    refunded = 10
    refund_pending = 11
    refund_failed = 12
    chargeback = 13


class APIError(Exception):
    pass


class PaymentRequestError(APIError):

    def __init__(self, status_code, error):
        self.status_code = status_code
        super().__init__('{}: {}'.format(status_code, error))


class Client(requests.Session):

    def __init__(self, api_key, api_secret, is_sandbox=True):
        super().__init__()
        self.api_key = api_key
        self.api_secret = api_secret
        self.is_sandbox = is_sandbox
        if is_sandbox:
            self.api_root = 'http://sandbox.payssion.com/api/v1'
        else:
            self.api_root = 'https://www.payssion.com/api/v1'

    def request(self, method, url, **kwargs):
        return super().request(method, self.api_root + url, **kwargs)

    def _raise_http_error(self, resp):
        raise APIError('{}: {}'.format(
            resp.status_code, resp.text
        ))

    def payment_details(self, transaction_id, order_id):
        """
        get payment details

        Example return value:

            {
                "todo":"redirect",
                "redirect_url":"https://www.payssion.com.com/E806897643289185",
                "transaction": {
                    "transaction_id":"E806897643289185",
                    "state":"pending",
                    "amount":"10.00",
                    "currency":"USD",
                    "order_id":""
                },
                "result_code":200
            }

        """
        resp = self.post('/payment/details', data={
            'api_key': self.api_key,
            'transaction_id': transaction_id,
            'order_id': order_id,
            'api_sig': self._get_signature(transaction_id, order_id),
        })
        if resp.status_code == 200:
            data = resp.json()
            result_code = data['result_code']
            if result_code == 200:
                return data
            elif result_code == 404:
                return None
            else:
                raise APIError('{}: {}'.format(resp.result_code, data))
        else:
            self._raise_http_error(resp)

    def payment_request(
            self, amount, currency, pm_id, description, order_id,
            return_url=None):
        """
        create payment

        Example return value:

            {
                "transaction": {
                    "transaction_id": "E806897643289185",
                    "state": "pending",
                    "amount": "10.00",
                    "currency": "USD",
                    "order_id": "123"
                },
                "result_code": 200
            }

        """
        amount = '{:.2f}'.format(amount)  # 2 places after decimal point
        order_id = str(order_id)

        data = {
            'api_key': self.api_key,
            'pm_id': pm_id,
            'amount': amount,
            'currency': currency,
            'description': description,
            'order_id': order_id,
            'api_sig': self._get_signature(pm_id, amount, currency, order_id)
        }
        if return_url:
            data['return_url'] = return_url
        resp = self.post('/payment/create', data=data)
        if resp.status_code == 200:
            # payssion retards wrap the status code in json body instead
            # simply using http status code.. sign..
            data = resp.json()
            if data['result_code'] == 200:
                return data
            else:
                raise PaymentRequestError(
                    data['result_code'], data.get('description'))
        else:
            self._raise_http_error(resp)

    def _get_signature(self, *args):
        parts = [self.api_key] + [str(a) for a in args] + [self.api_secret]
        return hashlib.md5('|'.join(parts).encode()).hexdigest()

    def verify_notify_signature(
            self, pm_id, amount, currency, order_id, state, signature):
        return hmac.compare_digest(  # avoid timing analysis
            signature,
            self._get_signature(pm_id, amount, currency, order_id, state)
        )
