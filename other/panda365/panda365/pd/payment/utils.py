from flask import abort
from pd.payment.models import Payment
import uuid


def make_ref_id():
    return uuid.uuid4().hex


def get_db_payment(**filters):
    """
    get payment from db. Lock it for update
    """
    obj = Payment.query.filter_by(**filters).with_for_update().first()
    if not obj:
        abort(404)
    return obj


def almost_equal(a, b, tolerance):
    return abs(a - b) <= tolerance
