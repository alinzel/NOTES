from decimal import Decimal
from .client import PaymentRequestError, APIError
from .client import PaymentStatus as PayssionPaymentStatus
from .schema import (
    CheckoutSchema, NotifySchema, PaymentSchema, TransactionSchema,
    CallbackSchema,
)
from flask import Blueprint, abort, url_for, current_app, redirect
from flask_babelex import gettext as _
from pd.api import abort_json, io_annotated
from pd.auth.jwt import auth_required, current_user_data
from pd.ext import payssion, limiter
from pd.payment import signals
from pd.payment.models import Payment, PaymentStatus, Vendors
from pd.payment.utils import make_ref_id, get_db_payment, almost_equal
from pd.sqla import db


api = Blueprint(
    'payments_payssion', __name__, url_prefix='/v1/payments/payssion')

_trans_schema = TransactionSchema()


@api.route('/', methods=['POST'])
@auth_required
@limiter.limit_and_check(
    # 预防double post
    '1/2 second',
    key_func=lambda: 'users/{}/payssion'.format(  # pragma: no cover
        current_user_data['id'],
    )
)
@io_annotated
def post(**data: CheckoutSchema()) -> PaymentSchema():
    """
    创建一个payssion payment. 返回值中包含一个**payment_url**, 客户端应使用
    它来为用户发起支付流程。支付流程:

    * 客户端通过请求发起支付: `POST /v1/payments/paypal/`
    * 返回值中包含支付连接**payment_url**, 客户端应将用户redirect到该地址进行支付
    * 用户完成支付后(无论成功、取消或失败)，客户端将被redirect回API server. API
      server将根据支付结果为用户加钱
    * 如果用户确认进行了支付，客户端将被跳转回`return_url`, 并在其query上包含
      了支付状态。例如: `app://payment_return/?status=pending`. 其中status可能
      的值包括: `pending`, `success`, `canceled`, `error`, `failed`, `expired`
    """
    order = data['order']
    ref_id = make_ref_id()
    req = dict(
        amount=order.amount,
        currency=str(order.currency),
        pm_id=data['method'],
        description=_('Order {}').format(order.id),
        order_id=ref_id,
        return_url=url_for('.callback', _external=True)
    )
    try:
        payment = payssion.client.payment_request(**req)
    except PaymentRequestError:
        current_app.logger.exception(
            'failed to create payssion payment %s', req)
        abort_json(500, 'failed to create payssion payment')
    else:
        current_app.logger.info(
            'successfully created payssion payment for order %d: %s',
            order.id, payment
        )
        assert payment['todo'] == 'redirect'
        assert payment['transaction']['state'] == 'pending'
        db_payment = Payment(
            object=order,
            amount=order.amount,
            currency=order.currency,
            vendor=Vendors.payssion,
            transaction_id=payment['transaction']['transaction_id'],
            ref_id=ref_id,
            # note this is what the user is paying, not the amount of gold
            method=data['method'],
            extra_data=payment,
            return_url=data['return_url'],
            user_id=current_user_data['id'],
        )
        signals.payment_created.send(db_payment)
        db.session.add(db_payment)
        db.session.commit()
        return db_payment


def _handle_payment(transaction, db_payment):
    state = transaction['state']
    current_app.logger.info(
        'handle payment %s: %s', transaction, state.name)

    new_status = None
    if state == PayssionPaymentStatus.completed:
        # verify amount paid
        amount_paid = Decimal(transaction['amount'])
        if not almost_equal(
                db_payment.amount, amount_paid, Decimal('0.001')):
            current_app.logger.error(
                'payssion payment amount verification failed; '
                'expected: %s, got: %s',
                db_payment.amount, amount_paid)
            db_payment.status = new_status = PaymentStatus.error
        elif db_payment.currency != transaction['currency']:
            current_app.logger.error(
                'payssion payment currency verification failed; '
                'expected: %s, got: %s',
                db_payment.currency, transaction['currency'])
            db_payment.status = new_status = PaymentStatus.error
            signals.payment_error.send(db_payment)
        else:
            db_payment.status = new_status = PaymentStatus.success
            signals.payment_succeeded.send(db_payment)
    if not new_status:
        if state in (
            PayssionPaymentStatus.cancelled,
            PayssionPaymentStatus.cancelled_by_user,
        ):
            db_payment.status = new_status = PaymentStatus.canceled
            signals.payment_canceled.send(db_payment)
        elif state == PayssionPaymentStatus.error:
            db_payment.status = new_status = PaymentStatus.error
            signals.payment_failed.send(db_payment)
        elif state in (
            PayssionPaymentStatus.failed,
            PayssionPaymentStatus.expired,
        ):
            db_payment.status = new_status = PaymentStatus.failed
            signals.payment_failed.send(db_payment)
        else:
            current_app.logger.error(
                'cannot handle this state of payssion payment: %s; '
                'cowardly refusing to do anything to the db payment',
                state, extra={'stack': True}
            )
    db_payment.extra_data['transaction'] = _trans_schema.dump(transaction).data
    return new_status


@api.route('/return')
@io_annotated
def callback(**data: CallbackSchema()):
    transaction_id = data['transaction_id']
    ref_id = data['order_id']
    db_payment = get_db_payment(
        transaction_id=transaction_id,
        ref_id=ref_id,
    )
    if db_payment.status != PaymentStatus.pending:
        # payment already sealed
        return redirect(db_payment.redirect_url)

    try:
        payment = payssion.client.payment_details(transaction_id, ref_id)
    except APIError:
        current_app.logger.exception(
            'failed to get payment detail for transaction %s', transaction_id)
        abort(500)
    if not payment:
        # this shouldn't happen since we found the payment in our db
        current_app.logger.error(
            'cannot find payment from payssion but it is in our db; '
            'payssion may have fucked up: transaction %s', transaction_id
        )
        abort(500)

    transaction = _trans_schema.load(payment['transaction']).data
    # new state coming
    state = transaction['state']

    if state == PayssionPaymentStatus.pending:
        # still pending; nothing changes
        current_app.logger.info(
            'payssion payment %s is pending in callback', transaction_id)
    else:
        # new status; handle it
        _handle_payment(transaction, db_payment)

    db.session.commit()

    return redirect(db_payment.redirect_url)


@api.route('/notify', methods=('POST',))
@io_annotated
def notify(**transaction: NotifySchema()):
    current_app.logger.info('payssion notified: %s', transaction)
    # no need to handle pending
    if transaction['state'] == PayssionPaymentStatus.pending:
        current_app.logger.info(
            'payssion payment %s is still pending; skip', transaction)
        return 'ok', 200
    db_payment = get_db_payment(ref_id=transaction['order_id'])
    # only handle if db payment is not finalized
    if db_payment.status == PaymentStatus.pending:
        _handle_payment(transaction, db_payment)
        db.session.commit()
    return 'ok', 200
