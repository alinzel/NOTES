import arrow
from enum import Enum
import sqlalchemy_utils as su
from sqlalchemy import func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.dialects.postgresql import JSONB
from pd.constants import Country
from pd.sqla import (
    TimestampMixin, db, translation_hybrid,
)


class Tip(db.Model):
    message_translations = db.Column(JSONB)
    message = translation_hybrid(message_translations)

    @classmethod
    def random(cls):
        return Tip.query.order_by('random()').first()

    def __repr__(self):
        return self.message


class WishMedia(db.Model):
    url = db.Column(db.Text, nullable=False)
    wish_id = db.Column(
        db.Integer, db.ForeignKey('wish.id', ondelete='CASCADE'),
        nullable=False,
    )
    wish = db.relationship(
        'Wish',
        backref=db.backref(
            'media', cascade='all, delete-orphan', passive_deletes=True,
            order_by='WishMedia.id',
        )
    )


class WishStatus(Enum):
    voting = 0
    finished = 1
    cancelled = 2


class Wish(TimestampMixin, db.Model):
    status = db.Column(
        su.ChoiceType(WishStatus, impl=db.SmallInteger()),
        default=WishStatus.voting, nullable=False,
    )
    message_translations = db.Column(JSONB)
    message = translation_hybrid(message_translations)
    # 商品信息
    info_translations = db.Column(JSONB)
    info = translation_hybrid(info_translations)
    votes_target = db.Column(
        db.Integer, nullable=False,
        doc='需要的总投票数',
    )
    tip_id = db.Column(
        db.Integer, db.ForeignKey('tip.id'), nullable=False,
    )
    tip = db.relationship('Tip', lazy='joined')

    my_vote = db.relationship('Vote', lazy='noload', uselist=False)

    admin_votes_num = db.Column(db.Integer, server_default='0', default=0)

    @su.aggregated('votes', db.Column(db.Integer, doc='当前投票数', default=0))
    def real_votes_num(self):
        return db.func.sum(Vote.count)

    @hybrid_property
    def votes_num(self):
        """
        current votes_num is the sum of:
        1. real votes from users
        2. a number set by admin
        """
        return min(
            self.votes_target, self.admin_votes_num + self.real_votes_num)

    @votes_num.expression
    def votes_num(cls):
        return func.least(
            cls.votes_target, cls.admin_votes_num + cls.real_votes_num)

    comments = db.relationship(
        'Comment',
        primaryjoin=(
            "and_(Comment.parent_id == foreign(Wish.id), Comment.parent_type == 'Wish')"  # noqa
        ),
        uselist=True,
        single_parent=True,
        cascade='all, delete-orphan',
    )

    @su.aggregated('comments', db.Column(db.Integer, doc='评论数', default=0))
    def comments_num(self):
        return db.func.count('1')

    @property
    def media_urls(self):
        return [m.url for m in self.media]

    @hybrid_property
    def vote_progress(self):
        return self.votes_num / self.votes_target

    @vote_progress.expression
    def vote_progress(cls):
        # we need to cast votes_target to float before division
        return cls.votes_num / func.cast(cls.votes_target, db.Float)

    @property
    def can_vote(self):
        return (
            self.status == WishStatus.voting and
            self.votes_num < self.votes_target
        )

    @property
    def country_price(self):
        if self.prices:
            return self.prices[0]

    def __str__(self):
        return '[{}]{}'.format(
            self.id, self.message[:20] if self.message else '')


class WishPrice(db.Model):
    country = db.Column(
        su.ChoiceType(Country, impl=db.Text()), nullable=False)
    price = db.Column(db.Float, nullable=False)
    currency = db.Column(su.CurrencyType, nullable=False)
    wish_id = db.Column(
        db.Integer, db.ForeignKey('wish.id', ondelete='CASCADE'),
        nullable=False,
    )
    wish = db.relationship(
        'Wish',
        backref=db.backref(
            'prices', cascade='all, delete-orphan', passive_deletes=True,
        )
    )

    def __repr__(self):
        return '[{}]{} {}'.format(self.country, self.price, self.currency)


class Vote(db.Model):
    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'),
        nullable=False,
    )
    user = db.relationship(
        'User',
        backref=db.backref(
            'votes', cascade='all, delete-orphan', passive_deletes=True,
        )
    )
    wish_id = db.Column(
        db.Integer, db.ForeignKey('wish.id', ondelete='CASCADE'),
        nullable=False,
    )
    wish = db.relationship(
        'Wish',
        backref=db.backref(
            'votes', cascade='all, delete-orphan', passive_deletes=True,
        )
    )
    count = db.Column(db.Integer, default=1, doc='用户在此wish上的总投票数')
    updated_at = db.Column(
        su.ArrowType, default=arrow.utcnow,
        doc='最近一次投票的时间'
    )
    __table_args__ = (
        db.UniqueConstraint('user_id', 'wish_id', name='uq_vote_wish_user'),
    )

    @property
    def next_vote_at(self):
        return self.updated_at.shift(days=1)

    @property
    def can_vote(self):
        return arrow.utcnow() > self.next_vote_at

    @classmethod
    def vote(cls, wish_id, user_id):
        obj = Vote.query.filter_by(
            user_id=user_id, wish_id=wish_id,
        ).with_for_update().first()
        if obj:
            if obj.can_vote:
                obj.count = obj.__table__.c.count + 1
                obj.updated_at = arrow.utcnow()
            else:
                return None
        else:
            obj = Vote(user_id=user_id, wish_id=wish_id)
            db.session.add(obj)
        return obj
