from unittest.mock import patch
import pytest
from pd.facebook.factory import CommentFactory, PostFactory
from pd.facebook.models import Comment
from pd.facebook.signal_handlers import (
    add_comment, edit_comment, remove_comment,
)

pytestmark = pytest.mark.db


@pytest.fixture
def mock_sync_fb_file():
    with patch(
            'pd.facebook.signal_handlers.comments.sync_fb_static_file') as m:
        m.return_value = 'https://test.com/uuid_400_600.jpg'
        yield m


@pytest.mark.parametrize('post_exists', [True, False])
def test_create_comment(post_exists, default_kwargs):
    data = {
        "item": "comment",
        "sender_name": "Carol Kim",
        "comment_id": "288731331545014_288738774877603",
        "sender_id": 1914154345481707,
        "post_id": "286247441793403_288731331545014",
        "verb": "add",
        "parent_id": "286247441793403_288731331545014",
        "created_time": 1489998669,
        "message": "I"
    }
    if post_exists:
        post = PostFactory(fb_id=data['post_id'])
        comments_num = post.comments_num
        comment = add_comment(data, **default_kwargs)
        assert comment
        assert comment.parent == post
        assert comment.fb_id == '288731331545014_288738774877603'
        assert comment.user.name == 'Carol Kim'
        assert comment.user.fb_id == '1914154345481707'
        assert comment.message == 'I'
        assert comment.created_at.timestamp == 1489998669
        assert post.comments.all() == [comment]
        assert post.comments_num == comments_num + 1
    else:  # should just ignore if the post does not exist
        assert not add_comment(data, **default_kwargs)
        assert not Comment.query.first()


def test_create_comment_with_one_photo(default_kwargs, mock_sync_fb_file):
    data = {
        "post_id": "286247441793403_288731331545014",
        "sender_name": "Carol Kim",
        "photo": "http://fb-s-c-a.akamaihd.net/h-ak-xal1/v/t1.0-9/17362800_1914154618815013_6405514220269587594_n.jpg?oh=bb8b01d6272ca1cf97fba380058a0689&oe=59569F39&__gda__=1499620098_e15d2472dba6926b60e4adefe53b9b6c",  # noqa
        "comment_id": "288731331545014_288739011544246",
        "sender_id": 1914154345481707,
        "item": "comment",
        "verb": "add",
        "parent_id": "286247441793403_288731331545014",
    }
    PostFactory(fb_id=data['post_id'])
    comment = add_comment(data, **default_kwargs)
    assert not comment.message
    assert mock_sync_fb_file.call_args[0][0] == data['photo']


@pytest.mark.parametrize('comment_exists', [True, False])
def test_edit_comment(comment_exists, default_kwargs):
    data = {
        "item": "comment",
        "sender_name": "Carol Kim",
        "comment_id": "288731331545014_288738774877603",
        "sender_id": 1914154345481707,
        "post_id": "286247441793403_288731331545014",
        "verb": "edited",
        "parent_id": "286247441793403_288731331545014",
        "created_time": 1489998692,
        "message": "I don't"
    }
    if comment_exists:
        existing_comment = CommentFactory(
            fb_id=data['comment_id'],
            parent__fb_id=data['post_id'],
        )
        post = existing_comment.parent
        comments_num = post.comments_num
        assert edit_comment(data, **default_kwargs)
        assert existing_comment.message == "I don't"
        assert post.comments_num == comments_num
    else:
        assert not edit_comment(data, **default_kwargs)
        assert not Comment.query.first()


@pytest.mark.parametrize('comment_exists', [True, False])
def test_delete_comment(comment_exists, default_kwargs):
    data = {
        "parent_id": "286247441793403_288731331545014",
        "sender_name": "Carol Kim",
        "comment_id": "288731331545014_288738774877603",
        "sender_id": 1914154345481707,
        "post_id": "286247441793403_288731331545014",
        "verb": "remove",
        "item": "comment",
        "created_time": 1489998713
    }
    if comment_exists:
        existing_comment = CommentFactory(
            fb_id=data['comment_id'],
            parent__fb_id=data['post_id'],
        )
        post = existing_comment.parent
        comments_num = post.comments_num
        assert remove_comment(data, **default_kwargs)
        assert not Comment.fb_query(data['comment_id']).first()
        assert post.comments_num == comments_num - 1
    else:
        assert not remove_comment(data, **default_kwargs)
    assert not Comment.query.first()
