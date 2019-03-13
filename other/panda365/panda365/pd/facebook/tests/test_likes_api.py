import pytest
from pd.test_utils import assert_dict_like
from pd.facebook.models import Base
from pd.facebook.factory import CommentFactory, PostFactory, UserFactory
from pd.facebook.api.likes import (
    post_likes_create, comment_likes_create, likes_list, likes_delete,
)


def test_auth():
    for v in (
        post_likes_create,
        comment_likes_create,
        likes_list,
        likes_delete,
    ):
        assert v._auth_required


@pytest.mark.parametrize('parent_factory', [
    PostFactory, CommentFactory
])
@pytest.mark.parametrize('trailing_slash', [True, False])
def test_likes_create(client, user, parent_factory, trailing_slash):
    client.login(user)
    parent = parent_factory()
    url_tpl = '/v1/{}s/{{}}/likes'.format(parent.__tablename__)
    if trailing_slash:
        url_tpl += '/'
    # can create
    likes_num = parent.likes_num
    resp = client.post(url_tpl.format(parent.id))
    assert resp.status_code == 200
    like = parent.likes.one()
    assert_dict_like(resp.json, {
        'id': like.id,
        'parent_gid': like.parent.gid,
    })
    # likes num should be incremented
    assert parent.likes_num == likes_num + 1
    assert user.likes == [like]
    # calling create the second time should be a no-op
    resp = client.post(url_tpl.format(parent.id))
    assert resp.status_code == 200
    assert resp.json['id'] == like.id
    assert parent.likes_num == likes_num + 1

    # 404
    resp = client.post(url_tpl.format(123123123123))
    assert resp.status_code == 404


@pytest.fixture
def parents():
    return [PostFactory(), CommentFactory()]


@pytest.fixture
def likes(user, parents):
    return [p.add_like(user=user) for p in parents]


def test_likes_list(client, user, likes, parents):
    # 3 likes in db, 2 are created by me
    other_user = UserFactory()
    parents[0].add_like(user=other_user)

    client.login(user)
    url = '/v1/likes/'

    # filter likes by parent gid
    resp = client.get(url, query_string={  # can use query as parameter
        'parent_gids': parents[0].gid,
    })
    assert resp.status_code == 200
    assert len(resp.json['objects']) == 1
    like = user.likes[0]
    assert_dict_like(resp.json['objects'][0], {
        'parent_gid': parents[0].gid,
        'id': like.id,
        '_type': 'like',
    })

    # parent can be given multiple times
    resp = client.get(url, json={  # can use json as parameter
        'parent_gids': [p.gid for p in parents]
    })
    assert resp.status_code == 200
    assert len(resp.json['objects']) == 2

    # works without any filter
    resp = client.get(url)
    assert resp.status_code == 200
    assert len(resp.json['objects']) == 2

    # parent type other than post and comment are ignored
    resp = client.get(url, json={
        'parent_gids': Base.encode_gid('Like', 1)
    })
    assert resp.status_code == 200
    assert len(resp.json['objects']) == 0

    # invalid gid
    resp = client.get(url, json={
        'parent_gids': ['adsfasd'],
    })
    assert resp.status_code == 422
    assert 'invalid gid' in str(resp.json['errors']['parent_gids'])


def test_likes_delete(client, user, likes, parents):
    # other user
    other_user = UserFactory()
    other_like = parents[0].add_like(user=other_user)

    client.login(user)
    url_tpl = '/v1/likes/{}'

    # like not found
    resp = client.delete(url_tpl.format(123121443))
    assert resp.status_code == 404
    assert 'Like 123121443 not found' in resp.json['message']

    # can delete my own like
    for like in likes:
        likes_num = like.parent.likes_num
        resp = client.delete(url_tpl.format(like.id))
        assert resp.status_code == 204
        assert like.parent.likes_num == likes_num - 1
        # already deleted
        resp = client.delete(url_tpl.format(like.id))
        assert resp.status_code == 404
        assert like.parent.likes_num == likes_num - 1

    # cannot delete other's like
    resp = client.delete(url_tpl.format(other_like.id))
    # since I can't see other's like, it's a 404 to me
    assert resp.status_code == 404
