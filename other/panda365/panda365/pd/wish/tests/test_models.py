from sqlalchemy_utils import sort_query
from pd.facebook.factory import CommentFactory, PostFactory, UserFactory
from pd.wish.models import Wish, WishStatus
from pd.wish.factory import WishFactory, WishPriceFactory, VoteFactory


def test_comments_num(db_session, user):
    wish = WishFactory()
    post = PostFactory(id=wish.id)
    assert wish.comments_num == 0
    CommentFactory(parent=wish, user=user)
    assert wish.comments_num == 1
    # comment on other types of parent should not affect wish
    CommentFactory(parent=post, user=user)
    db_session.commit()
    assert wish.comments_num == 1
    assert len(wish.comments) == 1


def test_vote_num(db_session, user):
    wish = WishFactory()
    assert wish.votes_num == 0
    VoteFactory(wish=wish, user=UserFactory())
    assert wish.votes_num == 1
    # votes by user 2
    vote2 = VoteFactory(wish=wish, user=user)
    assert wish.votes_num == 2
    vote2.count += 1
    db_session.commit()
    assert wish.votes_num == 3


def test_vote_progress(db_session, user):
    wish1 = WishFactory(votes_target=100)
    wish2 = WishFactory(votes_target=101)
    VoteFactory(wish=wish1, user=user)
    VoteFactory(wish=wish2, user=user)
    assert wish1.vote_progress > wish2.vote_progress
    q = Wish.query
    # vote_progress should be a float in db
    assert sort_query(
        q, 'vote_progress').all() != sort_query(q, '-vote_progress').all()


def test_wish_can_vote(db_session, user):
    wish = WishFactory(votes_target=1)
    assert wish.can_vote
    wish.status = WishStatus.cancelled
    assert not wish.can_vote

    wish.status = WishStatus.voting
    VoteFactory(wish=wish, user=user)
    assert not wish.can_vote


def test_wish_country_price(db_session):
    wish = WishFactory(prices=None)
    assert wish.country_price is None

    WishPriceFactory(wish=wish)
    assert wish.country_price == wish.prices[0]


def test_wish_manual_votes(db_session, user):
    wish = WishFactory(votes_target=3)
    assert wish.admin_votes_num == 0
    assert wish.real_votes_num == 0
    assert wish.votes_num == 0
    # one real vote
    VoteFactory(wish=wish, user=user)
    assert wish.real_votes_num == 1
    assert wish.votes_num == 1
    # admin sets an initial vote number
    wish.admin_votes_num = 1
    assert wish.votes_num == 2
    # votes_num cannot be greater than votes_target
    wish.admin_votes_num = 1000
    assert wish.votes_num == wish.votes_target
