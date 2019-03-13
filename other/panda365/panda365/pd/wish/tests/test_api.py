import arrow
from unittest.mock import patch
from pd.constants import Country
from pd.test_utils import assert_dict_like, assert_sorted_by
from pd.facebook.factory import UserFactory
from pd.facebook.tests.test_comments_api import _assert_comment_schema
from pd.wish.api import (
    wishes_list, vote_create, voted_wishes_list, comment_create,
)
from pd.wish.factory import WishFactory, VoteFactory
from pd.wish.models import Vote, WishStatus
import pytest


def test_auth():
    for view in (
        vote_create,
        comment_create,
        voted_wishes_list,
    ):
        assert view._auth_required
    assert wishes_list._auth_optional


@pytest.mark.parametrize('do_login', [False, True])
def test_wishes_list(db_session, client, user, do_login):
    # 3 wishes: 0, 1, 2;
    # user 1 has one vote in wish 1 and 2
    # user 2 has 2 votes in wish 2
    wishes = WishFactory.create_batch(3)
    user2 = UserFactory()
    VoteFactory(count=2, wish=wishes[-1], user=user2)
    for w in wishes[1:]:
        VoteFactory(wish=w, user=user)
    # the API can be accessed w/wo authentication
    if do_login:
        client.login(user)
    resp = client.get('/v1/wishes/')
    assert resp.status_code == 200
    assert len(resp.json['objects']) == 3
    # should be ordered by created_at descendingly
    assert_sorted_by(resp.json['objects'], '-created_at')
    # object schema
    returned_wish = resp.json['objects'][0]
    db_wish = wishes[-1]
    assert_dict_like(returned_wish, dict(
        id=db_wish.id,
        created_at=db_wish.created_at.isoformat(),
        message=db_wish.message_translations['en'],
        tip=db_wish.tip.message_translations['en'],
        media_urls=db_wish.media_urls,
        votes_num=db_wish.votes_num,
        votes_target=db_wish.votes_target,
        status='voting',
        comments_num=db_wish.comments_num,
    ))
    # product info
    info = db_wish.info_translations['en']
    k, v = info.split(':')
    assert returned_wish['info'] == [{
        'name': k.strip(),
        'value': v.strip(),
    }]
    if do_login:
        # user voted once on wish 2
        last_vote = Vote.query.filter_by(wish=db_wish, user=user).first()
        assert_dict_like(returned_wish['my_vote'], dict(
            id=last_vote.id,
            can_vote=last_vote.can_vote,
            count=last_vote.count,
            updated_at=last_vote.updated_at.isoformat(),
            next_vote_at=last_vote.next_vote_at.isoformat(),
        ))
        # wish without vote
        assert resp.json['objects'][-1]['my_vote'] is None
    else:
        assert returned_wish['my_vote'] is None


def test_country_filter(db_session, client):
    wishes = [WishFactory(prices__country=c) for c in [Country.MY, Country.ID]]
    url = '/v1/wishes/'

    resp = client.get(url, query_string={'country': 'MY'})
    assert resp.status_code == 200
    assert len(resp.json['objects']) == 1
    my_wish = wishes[0]
    my_wish_price = my_wish.prices[0]
    returned_wish = resp.json['objects'][0]
    assert_dict_like(returned_wish, dict(
        id=my_wish.id,
        country_price=dict(
            country='MY',
            price=my_wish_price.price,
            currency=dict(code='USD'),
        )
    ))

    # invalid country
    resp = client.get(url, query_string={'country': 'CN'})
    assert resp.status_code == 422
    assert 'not a valid choice' in str(resp.json['errors']['country'])


def test_vote_wish(db_session, client, user):
    client.login(user)
    wish = WishFactory(votes_target=2)
    db_session.commit()
    url_tpl = '/v1/wishes/{}/votes/'

    # can vote
    resp = client.post(url_tpl.format(wish.id))
    assert resp.status_code == 200
    assert wish.votes_num == 1
    vote = Vote.query.filter_by(wish=wish, user=user).one()
    assert_dict_like(resp.json, dict(
        id=vote.id,
        updated_at=vote.updated_at.isoformat(),
        count=1,
    ))

    # cannot vote if status is not voting
    wish.status = WishStatus.cancelled
    resp = client.post(url_tpl.format(wish.id))
    assert resp.status_code == 409
    assert 'finished' in resp.json['message']

    # cannot vote again on the same day
    wish.status = WishStatus.voting
    resp = client.post(url_tpl.format(wish.id))
    assert resp.status_code == 409
    assert 'you can only vote once per wish each day' == resp.json['message']
    now = arrow.utcnow()
    with patch(
        'pd.wish.models.arrow.utcnow',
    ) as mock_now:
        mock_now.return_value = now.shift(days=1)
        # can vote 1 day later
        resp = client.post(url_tpl.format(wish.id))
        assert resp.status_code == 200
        assert wish.votes_num == 2
        # wish reached its vote target; should not allow votes any more
        mock_now.return_value = now.shift(days=3)
        resp = client.post(url_tpl.format(wish.id))
        assert resp.status_code == 409
        assert 'finished' in resp.json['message']

    # non-existent wish
    resp = client.post(url_tpl.format(12312313))
    assert resp.status_code == 404
    assert 'not found' in resp.json['message']


def test_wish_comments(db_session, client, user, png_data_url):
    wish = WishFactory()
    client.login(user)
    url = '/v1/wishes/{}/comments/'.format(wish.id)

    # can create comment
    resp = client.post(url, json=dict(message='blah', photo=png_data_url))
    assert resp.status_code == 200, resp.json
    db_session.refresh(wish)
    assert wish.comments_num == 1
    comment = wish.comments[0]
    assert comment.id == resp.json['id']

    # can list comments
    resp = client.get(url)
    assert resp.status_code == 200
    assert len(resp.json['objects']) == 1
    _assert_comment_schema(resp.json['objects'][0], comment)


def test_voted_wishes_list(db_session, client, user):
    # scenario: 2 wishes; user voted twice on wish 0
    wishes = WishFactory.create_batch(2)
    voted_wish = wishes[0]
    vote = VoteFactory(wish=voted_wish, user=user, count=2)

    # should only return the one voted wish
    client.login(user)
    url = '/v1/wishes/voted/'
    resp = client.get(url)
    assert resp.status_code == 200
    assert len(resp.json['objects']) == 1
    returned_wish = resp.json['objects'][0]
    assert_dict_like(returned_wish, dict(
        id=voted_wish.id,
        my_vote=dict(
            id=vote.id,
            count=2
        )
    ))
