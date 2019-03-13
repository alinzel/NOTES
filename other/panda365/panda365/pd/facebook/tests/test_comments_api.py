import pytest
from pd.facebook.models import Comment
from pd.facebook.factory import CommentFactory, PostFactory, ReplyFactory
from pd.facebook.api.comments import (
    comment_replies_create, post_comments_create,
)
from pd.test_utils import (
    assert_dict_like, assert_sorted_by,
)

pytestmark = pytest.mark.db


def test_auth():
    for v in (
            comment_replies_create,
            post_comments_create,
    ):
        assert v._auth_required


def _assert_comment_schema(json_obj, comment, check_replies=True):
    user = comment.user
    assert_dict_like(json_obj, {
        '_type': 'comment',
        'created_at': comment.created_at.isoformat(),
        'gid': comment.gid,
        'fb_id': comment.fb_id,
        'message': comment.message,
        'photo_url': comment.photo_url,
        'comments_num': comment.comments_num,
        'likes_num': comment.likes_num,
        'user': {
            'id': user.id,
            'gid': user.gid,
            'fb_id': user.fb_id,
            'name': user.name,
            'icon_url': user.icon_url,
        }
    })
    if check_replies:
        # post comment should include replies
        assert ('replies' not in json_obj) == comment.is_reply


@pytest.mark.parametrize('parent_factory', [PostFactory, CommentFactory])
def test_comments_list(client, user, parent_factory):
    (parent_with_comments,
     parent_without_comments) = parent_factory.create_batch(2)
    for _ in range(2):
        parent_with_comments.add_comment(user=user, message='hi')
    if parent_factory == PostFactory:
        url_tpl = '/v1/posts/{}/comments/'
    else:
        url_tpl = '/v1/comments/{}/replies/'

    # get post's comments
    resp = client.get(url_tpl.format(parent_with_comments.id))
    assert resp.status_code == 200
    assert_sorted_by(resp.json['objects'], '-created_at')
    assert len(resp.json['objects']) == 2
    obj = resp.json['objects'][0]
    comment = Comment.query.get(obj['id'])
    _assert_comment_schema(obj, comment)

    # post without comments
    resp = client.get(url_tpl.format(parent_without_comments.id))
    assert resp.status_code == 200
    assert resp.json['objects'] == []


def test_generic_comments_list(client, user):
    (parent_with_comments,
     parent_without_comments) = PostFactory.create_batch(2)
    parent_with_comments.add_comment(user=user, message='hi')
    url = '/v1/comments/'

    resp = client.get(url, query_string=dict(
        parent_type='Post', parent_id=parent_with_comments.id,
    ))
    assert resp.status_code == 200
    _assert_comment_schema(
        resp.json['objects'][0], parent_with_comments.comments[0])

    CommentFactory(is_active=False)
    resp = client.get(url, query_string=dict(
        parent_type='Post', parent_id=parent_with_comments.id,
    ))
    assert resp.status_code == 200


def test_post_comment_replies(config, monkeypatch, client, user):
    """
    each post comment should include its first page of replies
    """
    post = PostFactory()
    comments = CommentFactory.create_batch(2, parent=post)
    for c in comments:
        ReplyFactory.create_batch(3, parent=c)
    monkeypatch.setitem(config, 'API_PER_PAGE', 2)
    resp = client.get('/v1/posts/{}/comments/'.format(post.id))
    assert resp.status_code == 200
    assert len(resp.json['objects']) == 2
    obj = resp.json['objects'][0]
    assert 'replies' in obj
    assert len(obj['replies']) == 2
    assert_sorted_by(obj['replies'], '-created_at')
    reply_obj = obj['replies'][0]
    reply = Comment.query.get(reply_obj['id'])
    _assert_comment_schema(reply_obj, reply)


@pytest.mark.parametrize('parent_factory', [PostFactory, CommentFactory])
def test_create_comment(
        app, db_session, client, user, parent_factory, png_data_url):
    # setup parent
    parent = parent_factory()
    if parent_factory == PostFactory:
        url_tpl = '/v1/{}s/{{}}/comments/'.format(parent.__tablename__)
    else:
        url_tpl = '/v1/{}s/{{}}/replies/'.format(parent.__tablename__)
    url = url_tpl.format(parent.id)
    client.login(user)

    # should be able to create
    comments_num = parent.comments_num
    resp = client.post(url, json={
        'message': 'hi',
        'photo': png_data_url
    })
    assert resp.status_code == 200, resp.json
    assert parent.comments.count() == 1
    comment = parent.comments[0]
    assert_dict_like(resp.json, {
        'id': comment.id,
        'message': 'hi',
    })
    assert resp.json['photo_url'].startswith(
        'https://{}/images/comments/{}/'.format(
            app.config['S3_BUCKET'], comment.id))
    assert parent.comments_num == comments_num + 1
    assert user.comments == [comment]

    # should be able to create with only image or content
    for data in (
            {'message': 'hi'},
            {'photo': png_data_url},
    ):
        resp = client.post(url, json=data)
        assert resp.status_code == 200, resp.json

    # cannot create if both content and image are not given
    resp = client.post(url)
    assert resp.status_code == 422
    assert 'message and photo cannot both be empty' in str(
        resp.json['errors']['_schema'])

    # non-existent parent
    resp = client.post(url_tpl.format(123123123), json={'message': 'hi'})
    assert resp.status_code == 404, resp.json


def test_generic_comment_create(client, user, png_data_url):
    post = PostFactory()
    client.login(user)
    url = '/v1/comments/'
    default_data = dict(parent_type='Post', parent_id=post.id)

    # can create comment
    resp = client.post(url, data=dict(
        message='blah',
        **default_data
    ))
    assert resp.status_code == 200, resp.json
    _assert_comment_schema(resp.json, post.comments[0], False)

    # image upload
    resp = client.post(url, data=dict(
        photo=png_data_url,
        **default_data
    ))
    assert resp.status_code == 200

    # one of image or photo must be set
    resp = client.post(url, data=default_data)
    assert resp.status_code == 422
    assert 'message and photo cannot both be empty' in str(
        resp.json['errors']['_schema'])

    # invalid parent type
    resp = client.post(url, data=dict(parent_type='hi', parent_id=10))
    assert resp.status_code == 422
    assert 'not defined' in resp.json['errors']['parent_type'][0]
