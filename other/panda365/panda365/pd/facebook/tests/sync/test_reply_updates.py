import pytest
from pd.facebook.factory import CommentFactory
from pd.facebook.models import Comment
from pd.facebook.signal_handlers import add_comment, remove_comment


pytestmark = pytest.mark.db


def test_create_reply(default_kwargs):
    data = {
        "item": "comment",
        "sender_name": "Helms Zhang",
        "comment_id": "288731331545014_288739571544190",
        "sender_id": 1318834338230112,
        "post_id": "286247441793403_288731331545014",
        "verb": "add",
        "parent_id": "288731331545014_288739011544246",
        "created_time": 1489998935,
        "message": "The"
    }
    comment = CommentFactory(
        fb_id=data['parent_id'], parent__fb_id=data['post_id'])
    reply = add_comment(data, **default_kwargs)
    assert reply.parent == comment


def test_delete_reply(default_kwargs):
    data = {
        "parent_id": "288731331545014_288739011544246",
        "sender_name": "Helms Zhang",
        "comment_id": "288731331545014_288739571544190",
        "sender_id": 1318834338230112,
        "post_id": "286247441793403_288731331545014",
        "verb": "remove",
        "item": "comment",
        "created_time": 1489998988
    }
    CommentFactory(
        fb_id=data['parent_id'], parent__fb_id=data['post_id'])
    reply = add_comment(data, **default_kwargs)
    reply_id = reply.id
    assert remove_comment(data, **default_kwargs)
    assert not Comment.query.get(reply_id)
