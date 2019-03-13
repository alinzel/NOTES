from blinker import signal
from enum import Enum
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
import arrow
import sqlalchemy_utils as su
from sqlalchemy import func

from pd.constants import Country
from pd.sqla import CreateTimestampMixin, db, logger
from pd.groupon import signals
from pd.groupon.models.order import Order, OrderStatus
from pd.facebook.models import User


class BatchFinishStatus(Enum):
    pending = 1  # 批次正在进行，结束时间尚早
    scheduled = 2  # 批次正在进行，期次结束时间将近，结束处理任务已进入队列
    done = 3  # 批次已结束，且已经行了结束处理(标记期次完结等)


class BatchMixin(CreateTimestampMixin):
    # product attributes
    country = db.Column(
        su.ChoiceType(Country, impl=db.Text()), nullable=False,
    )

    @declared_attr
    def product_id(cls):
        return db.Column(
            db.Integer, db.ForeignKey('product.id'), nullable=False,
        )

    @declared_attr
    def product(cls):
        return db.relationship('Product')

    @declared_attr
    def category_id(cls):
        return db.Column(
            db.Integer, db.ForeignKey('category.id'), nullable=True,
        )

    @declared_attr
    def category(cls):
        return db.relationship('Category')

    price = db.Column(db.DECIMAL, nullable=False, doc='价格')
    currency = db.Column(su.CurrencyType, nullable=False)
    market_price = db.Column(db.DECIMAL, nullable=False, doc='市场价')
    market_currency = db.Column(su.CurrencyType, nullable=False)
    shipping_price = db.Column(db.DECIMAL, default=0, nullable=False, doc='邮费')
    # game logic
    total_shares = db.Column(db.Integer, nullable=False, doc='团购份数')
    start_at = db.Column(
        su.ArrowType, default=arrow.utcnow, nullable=False, doc='团购开始时间')
    end_at = db.Column(su.ArrowType, nullable=False, doc='团购结束时间')
    direct_buy_url = db.Column(db.Text, doc='直接购买链接')
    sort_weight = db.Column(
        db.Float, default=0, server_default='0',
        doc='games are ordered according to their batch\'s sort_weight. '
            'games with larger sort_weight is ordered first'
    )


class Batch(BatchMixin, db.Model):
    # TODO: implement hybrid_property `is_running`; can be used by admin filter

    # 标记批次结束需要的处理是否已进行
    finish_status = db.Column(
        su.ChoiceType(BatchFinishStatus, impl=db.SmallInteger()),
        default=BatchFinishStatus.pending,
    )

    sold_num = db.Column(db.Integer, default=0)

    @hybrid_property
    def is_running(self):
        return self.start_at <= arrow.utcnow() < self.end_at

    @su.aggregated('games', db.Column(db.Integer, default=0))
    def games_count(self):
        return db.func.count('1')

    def create_game(self):
        game = Game(
            batch_id=self.id,
            left_shares=self.total_shares,
            issue_id=self.games_count + 1,
        )
        for col in (
            'country',
            'product_id',
            'category_id',
            'price',
            'currency',
            'market_price',
            'market_currency',
            'shipping_price',
            'total_shares',
            'start_at',
            'end_at',
            'direct_buy_url',
            'sort_weight',
        ):
            setattr(game, col, getattr(self, col))
        db.session.add(game)
        return game

    def get_latest_game(self, lock=False):
        q = Game.query.filter(
            Game.is_running,
            Game.batch_id == self.id,
        )
        if lock:
            q = q.with_for_update(of=Game)
        return q.first()

    def finish(self):
        if self.finish_status != BatchFinishStatus.done:
            self.finish_status = BatchFinishStatus.done
            signals.batch_finished.send(self)
            game = self.get_latest_game(lock=True)
            if game:  # pragma: no cover
                game.left_shares = 0
                signals.game_finished.send(game)
                return game

    def check_game_finish(self, game):
        """
        check if the given game is finished.

        If so, create new game if the batch is still running
        """
        if not game.is_running:
            signals.game_finished.send(game)
            if self.is_running:
                next_game = self.create_game()
                db.session.flush()
                logger.info(
                    'batch %d running, created next game: %d',
                    self.id, next_game.id
                )
            else:  # pragma: no cover
                # this only happens if the batch finishes exactly during
                # the execution from line `if game` to here
                logger.info(
                    'batch %d finished. No more games are created',
                    self.id
                )

    def purchase_game_share(self, order):
        """
        从此批次的期次中购买一个share。返回期次id.

        1. 获取最新期次，若存在，则game.left_shares -= 1
        2. 最新期次不存在，即批次已结束，则创建一个新game，其剩余份数设为0
        3. 若期次被购买完，则发送期次完结信号。此时若批次未结束，则生成新的期次

        这个函数会**锁**当前批次的最新期次
        """
        game = self.get_latest_game(lock=True)
        if game:
            # since we locked it, it's ok to read-and-write instead of using
            # a update query like
            # `update game set left_shares = left_shares - 1`
            order.game = game
            game.left_shares -= 1
            db.session.flush()
            self.check_game_finish(game)
        else:
            game = self.create_game()
            game.left_shares = 0
            order.game = game
            db.session.flush()  # get game id
            signals.game_finished.send(game)
            logger.info(
                'attempted to draw a share from a finished batch[%d]; a '
                'placeholder game is created for it: %d', self.id, game.id
            )
        logger.info(
            'a share is taken from game %d by order %d; left shares: %d',
            game.id, order.id, game.left_shares,
        )
        return game.id

    def __repr__(self):
        return '[{}]{}{}'.format(self.id, self.country, self.product)


batch_spec_option_assoc = db.Table(
    'batch_spec_options',
    db.Column('batch_spec_id', db.Integer, db.ForeignKey('batch_spec.id')),
    db.Column('spec_option_id', db.Integer, db.ForeignKey('spec_option.id')),
)


class BatchSpec(db.Model):
    batch_id = db.Column(
        db.Integer, db.ForeignKey('batch.id'), nullable=False,
    )
    batch = db.relationship('Batch', backref='specs')
    spec_id = db.Column(
        db.Integer, db.ForeignKey('spec.id'), nullable=False,
    )
    spec = db.relationship('Spec')
    options = db.relationship('SpecOption', secondary=batch_spec_option_assoc)

    def __repr__(self):
        return '[{}]{}{}'.format(self.id, self.spec, self.options)


class Game(BatchMixin, db.Model):
    """
    game与batch的字段大部分是相同的。因为可能存在批次进行中修改属性的情况(
    例如修改价格), 我们将batch的属性复制到game上，而不是使用join来读取
    """
    batch_id = db.Column(
        db.Integer, db.ForeignKey('batch.id'), nullable=False,
        doc='批次id',
    )
    batch = db.relationship('Batch', backref='games')
    left_shares = db.Column(db.Integer, nullable=False, doc='本期剩余份数')
    issue_id = db.Column(db.Integer, nullable=False)

    @hybrid_property
    def is_running(self):
        return (
            self.start_at <= arrow.utcnow() < self.end_at and
            self.left_shares > 0
        )

    @is_running.expression
    def is_running(cls):
        now = arrow.utcnow()
        return db.and_(
            cls.start_at <= now,
            cls.end_at > now,
            cls.left_shares > 0,
        )

    @property
    def sold_shares(self):
        return self.total_shares - self.left_shares

    @hybrid_property
    def groupon_progress(self):
        return self.sold_shares / self.total_shares

    @groupon_progress.expression
    def groupon_progress(cls):
        # we need to cast total_shares to float before division
        return (cls.total_shares - cls.left_shares) / \
            func.cast(cls.total_shares, db.Float)

    @property
    def sold_num(self):
        return self.batch.sold_num

    __table_args__ = (
        db.CheckConstraint(left_shares >= 0, name='left_shares_gte_0'),
    )

    def check_left_shares(self):
        """
        检查当前剩余份数中是否含有用户的已支付订单,如果没有则创建机器人订单
        """
        orders = Order.query.filter(
            Order.game == self,
            Order.status == OrderStatus.paid,
        ).all()
        if self.is_running and self.sold_shares > len(orders):
            users = User.query.filter_by(
                is_bot=True).order_by(func.random()
                                      ).limit(self.sold_shares-len(orders))
            for user in users:
                Order(
                    game=self,
                    user=user,
                    user_id=user.id,
                    email='bot',
                    full_name='bot',
                    complete_address='bot',
                    postcode='bot',
                    city='bot',
                    province='bot',
                    phone='bot',
                    status=OrderStatus.paid
                )
                db.session.flush()
            return len(users.all())

    @property
    def users(self):
        orders = Order.query.filter(
            Order.game == self, Order.status == OrderStatus.paid)
        return [o.user for o in orders]


payment_succeeded_signal = signal('payment_succeeded')


@payment_succeeded_signal.connect
def update_sold_num(payment):
    return Batch.query.filter(
        Batch.id == payment.order.batch_id,
    ).update({
        Batch.sold_num: Batch.sold_num + 1,
    })
