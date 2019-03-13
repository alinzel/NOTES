import arrow
from enum import Enum
from flask_babelex import lazy_gettext as _
from pd.groupon import signals as game_signals
from pd.payment import signals as payment_signals
from pd.payment.models import Payment
from pd.sqla import db, logger, TimestampMixin
import sqlalchemy_utils as su


class OrderStatus(Enum):
    payment_pending = 1
    payment_processing = 2
    payment_failed = 3
    paid = 4
    processing = 5
    shipped = 6
    canceled = 7


OrderStatus.payment_pending.label = _('payment_pending')
OrderStatus.payment_processing.label = _('payment_processing')
OrderStatus.payment_failed.label = _('payment_failed')
OrderStatus.paid.label = _('paid')
OrderStatus.processing.label = _('proccessing')
OrderStatus.shipped.label = _('shipped')
OrderStatus.canceled.label = _('canceled')


class AddressMixin:
    full_name = db.Column(db.Text, nullable=False)
    complete_address = db.Column(db.Text, nullable=False)
    postcode = db.Column(db.Text, nullable=False)
    city = db.Column(db.Text, nullable=False)
    province = db.Column(db.Text, nullable=False)
    phone = db.Column(db.Text, nullable=False)


class Order(AddressMixin, TimestampMixin, db.Model):
    """
    订单生命周期:
        1. 创建订单。此时订单至于批次关联，等待支付。
        2. 用户支付成功，订单与当前在售的期次关联，等待成团。
        3. 订单对应的期次销售完毕时，若订单尚未支付成功，则设为"取消"; 否则设
           为订单处理中

    一个用户在一个期次中只能参加一次。

    因为支付有延时，所以可能出现在支付完成时，订单原本的期次已经完成的情况.
    例如，用户u1在期次g1中创建了订单，在他支付过程中，g1被其他用户买光了。当
    支付完成时，系统应该获取订单对应批次的最新期次，并将其与订单关联。如果此时
    对应的批次已经结束，则继续在批次中创建一个期次给它.

    这意味着如果批次在运行过程中价格不能修改，否则可能出现价格与用户实际支付
    钱数不一致的情况。
    """
    email = db.Column(db.Text, nullable=False)
    status = db.Column(
        su.ChoiceType(OrderStatus, impl=db.SmallInteger()),
        default=OrderStatus.payment_pending,
    )

    batch_id = db.Column(
        db.Integer, db.ForeignKey('batch.id'), nullable=False,
    )
    batch = db.relationship('Batch', backref='orders')
    game_id = db.Column(
        db.Integer, db.ForeignKey('game.id'), nullable=False,
    )
    game = db.relationship('Game', backref='orders')
    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id'), nullable=False,
    )
    user = db.relationship('User', backref='orders')
    spec = db.Column(db.Text, nullable=True, doc='规格')
    quantity = db.Column(db.Integer, default=1, server_default='1')
    # 支付信息
    price = db.Column(db.DECIMAL, nullable=False)
    shipping_price = db.Column(db.DECIMAL, nullable=False)
    currency = db.Column(su.CurrencyType, nullable=False)
    payment = db.relationship(
        Payment, doc='successful payment for this order',
        primaryjoin=(
            "and_(Order.id == foreign(Payment.object_id), "
            "Payment.object_type == 'Order')"
        ),
        uselist=False,
    )

    def __init__(self, **kwargs):
        game = kwargs.get('game', None)
        if game:
            # set attributes related to game
            for k in (
                'batch',
                'price',
                'shipping_price',
                'currency',
            ):
                kwargs.setdefault(k, getattr(game, k))
        super().__init__(**kwargs)

    @property
    def amount(self):
        if self.price is not None and self.shipping_price is not None:
            return (self.price * self.quantity) + self.shipping_price

    def set_status(self, to_status, from_status):
        if self.status in from_status:
            from_ = self.status
            self.status = to_status
            logger.info(
                'order %d status updated from %s to %s',
                self.id, from_.name, to_status.name)
            db.session.flush()
            return to_status
        else:
            logger.warn(
                'status of order %d is not one of %s; skip setting it to %s',
                self.id, [s.name for s in from_status], to_status.name
            )

    UQ_USER_GAME = 'uq_order_game_user'

    __table_args__ = (
        # 一个用户在一个期次中只能参与一次
        db.UniqueConstraint(
            'game_id', 'user_id', name=UQ_USER_GAME,
        ),
    )


@payment_signals.payment_created.connect
def on_payment_created(payment):
    payment.object.set_status(
        OrderStatus.payment_processing, [
            # 尚未支付
            OrderStatus.payment_pending,
            # 支付失败后再次支付
            OrderStatus.payment_failed,
        ]
    )


@payment_signals.payment_succeeded.connect
def on_payment_succeeded(payment):
    order = payment.object
    order.set_status(OrderStatus.paid, [OrderStatus.payment_processing])
    # link game
    order.batch.purchase_game_share(order)


@payment_signals.payment_failed.connect
def on_payment_failed(payment):
    payment.object.set_status(
        OrderStatus.payment_failed, [OrderStatus.payment_processing])


@payment_signals.payment_canceled.connect
def on_payment_canceled(payment):
    payment.object.set_status(
        OrderStatus.canceled, [OrderStatus.payment_processing])


@game_signals.game_finished.connect
def on_game_finished(game):
    # set paid orders to processing
    Order.query.filter(
        Order.game_id == game.id,
        Order.status == OrderStatus.paid,
    ).update({
        Order.status: OrderStatus.processing,
        Order.updated_at: arrow.utcnow(),
    })
    # TODO: notify users and admin via email


@game_signals.batch_finished.connect
def on_batch_finished(batch):
    Order.query.filter(
        Order.batch_id == batch.id,
        Order.status == OrderStatus.payment_pending,
    ).update({
        Order.status: OrderStatus.canceled,
        Order.updated_at: arrow.utcnow(),
    })
