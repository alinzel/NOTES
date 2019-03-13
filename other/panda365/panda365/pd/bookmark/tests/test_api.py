from pd.test_utils import assert_dict_like
from pd.facebook.factory import PostFactory, UserFactory
from pd.bookmark.api import bookmarks_create, bookmarks_delete, bookmarks_list
from pd.bookmark.models import Bookmark
from pd.bookmark.factory import BookmarkFactory


def test_auth():
    for v in (
        bookmarks_create,
        bookmarks_delete,
        bookmarks_list,
    ):
        assert v._auth_required


def test_bookmarks_create(db_session, client, user):
    post = PostFactory()
    client.login(user)
    url_tpl = '/v1/posts/{}/bookmarks/'

    url = url_tpl.format(post.id)
    # can create
    resp = client.post(url)
    assert resp.status_code == 200
    bookmark = Bookmark.query.one()
    assert_dict_like(resp.json, dict(
        id=bookmark.id,
        post_id=bookmark.post_id,
    ))
    # calling post twice is a no-op
    resp = client.post(url)
    assert resp.status_code == 200
    assert Bookmark.query.one() == bookmark
    assert resp.json['id'] == bookmark.id
    # cannot create bookmark on non-existent post
    resp = client.post(url_tpl.format('12312313'))
    assert resp.status_code == 404
    assert 'does not exist' in resp.json['message']


def test_bookmarks_list_and_delete(db_session, client, user):
    posts = PostFactory.create_batch(2)
    bookmarks = [BookmarkFactory(post=post, user=user) for post in posts]
    user2 = UserFactory()
    u2_bookmark = BookmarkFactory(post=posts[0], user=user2)
    client.login(user)
    # get bookmarks by post id
    url = '/v1/bookmarks/'
    bookmark = bookmarks[0]
    for kwargs in (
        # post_ids can be passed in query or json
        dict(query_string={'post_ids': bookmark.post_id}),
        dict(json={'post_ids': [bookmark.post_id]}),
    ):
        resp = client.get(url, **kwargs)
        assert resp.status_code == 200
        assert len(resp.json['objects']) == 1
        assert_dict_like(resp.json['objects'][0], {
            'id': bookmark.id,
            'post_id': bookmark.post_id,
        })
    # should return all bookmarks if no post_id given
    resp = client.get(url)
    assert resp.status_code == 200
    assert {o['id'] for o in resp.json['objects']} == {b.id for b in bookmarks}

    # delete bookmark
    url = url + '{}'
    resp = client.delete(url.format(bookmark.id))
    assert resp.status_code == 204
    assert not Bookmark.query.get(bookmark.id)
    # cannot delete others' bookmark
    resp = client.delete(url.format(u2_bookmark.id))
    assert resp.status_code == 404
    assert Bookmark.query.get(u2_bookmark.id)
