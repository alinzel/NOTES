import pytest
from pd.facebook.factory import CommentFactory, PostFactory
from pd.facebook.models import Like
from pd.facebook.signal_handlers import add_like, remove_like


pytestmark = pytest.mark.db


@pytest.mark.parametrize('post_exists', [True, False])
def test_like_post(post_exists, default_kwargs):
    """
    点like或reactions时会触发两个update
    一个是like，一个是reaction

    现在reaction先忽略
    """
    # XXX: reaction is ignored for now
    # change = {
    #     "field": "feed",
    #     "value": {
    #         "reaction_type": "like",
    #         "parent_id": "286247441793403_288731331545014",
    #         "sender_name": "Carol Kim",
    #         "sender_id": 1914154345481707,
    #         "post_id": "286247441793403_288731331545014",
    #         "verb": "add",
    #         "item": "reaction",
    #         "created_time": 1489999084
    #     }
    # }

    data = {
        "parent_id": "286247441793403_288731331545014",
        "sender_name": "Carol Kim",
        "sender_id": 1914154345481707,
        "post_id": "286247441793403_288731331545014",
        "verb": "add",
        "item": "like",
        "created_time": 1489999084
    }

    if post_exists:
        post = PostFactory(fb_id=data['post_id'])
        likes_num = post.likes_num
        like = add_like(data, **default_kwargs)
        assert like
        assert like.parent == post
        # like's doesn't have fb_ids; we use (post_id + sender_id)
        assert like.fb_id == '286247441793403_288731331545014_1914154345481707'
        assert like.user.name == 'Carol Kim'
        assert like.user.fb_id == '1914154345481707'
        assert like.created_at.timestamp == 1489999084
        assert post.likes.all() == [like]
        assert post.likes_num == likes_num + 1
    else:
        assert not add_like(data, **default_kwargs)
        assert not Like.query.first()


# def test_edit_reaction_post():
#     """
#     edit reactions时只会产生一个reaction的update
#     """
#     change = {
#         "field": "feed",
#         "value": {
#             "reaction_type": "love",
#             "parent_id": "286247441793403_288728671545280",
#             "sender_name": "Carol Kim",
#             "sender_id": 1914154345481707,
#             "post_id": "286247441793403_288728671545280",
#             "verb": "edit",
#             "item": "reaction",
#             "created_time": 1489999284
#         }
#     }


@pytest.mark.parametrize('post_exists', [True, False])
@pytest.mark.parametrize('post_liked', [True, False])
def test_unlike_post(post_exists, post_liked, default_kwargs):
    """
    同添加like，delete也会触发两个事件
    """
    data = {
        "parent_id": "286247441793403_288728671545280",
        "sender_name": "Carol Kim",
        "sender_id": 1914154345481707,
        "post_id": "286247441793403_288728671545280",
        "verb": "remove",
        "item": "like",
        "created_time": 1489999293
    }
    if post_exists:
        # setup
        post = PostFactory(fb_id=data['post_id'])
        if post_liked:
            add_like(data, **default_kwargs)

        likes_num = post.likes_num
        removed = remove_like(data, **default_kwargs)
        assert removed == post_liked
        assert post.likes_num == (likes_num - 1 if post_liked else likes_num)
        assert not post.likes.all()
    else:
        assert not remove_like(data, **default_kwargs)


@pytest.mark.parametrize('comment_exists', [True, False])
def test_like_reply_or_comment(comment_exists, default_kwargs):
    data = {
        "sender_name": "Panda365",
        "comment_id": "288731331545014_288739908210823",
        "sender_id": 286247441793403,
        "item": "like",
        "verb": "add",
    }
    if comment_exists:
        comment = CommentFactory(fb_id=data['comment_id'])
        likes_num = comment.likes_num
        like = add_like(data, **default_kwargs)
        assert like
        assert like.fb_id == '288731331545014_288739908210823_286247441793403'
        assert like.parent == comment
        assert like.user.name == 'Panda365'
        assert like.user.fb_id == '286247441793403'
        assert comment.likes.all() == [like]
        assert comment.likes_num == likes_num + 1
    else:
        assert not add_like(data, **default_kwargs)
        assert not Like.query.first()


@pytest.mark.parametrize('comment_exists', [True, False])
@pytest.mark.parametrize('comment_liked', [True, False])
def test_unlike_reply_or_comment(
        comment_exists, comment_liked, default_kwargs):
    data = {
        "sender_name": "Panda365",
        "comment_id": "288731331545014_288739908210823",
        "sender_id": 286247441793403,
        "item": "like",
        "verb": "remove",
        "created_time": 1490077184
    }
    if comment_exists:
        comment = CommentFactory(fb_id=data['comment_id'])
        if comment_liked:
            add_like(data, **default_kwargs)
        likes_num = comment.likes_num
        removed = remove_like(data, **default_kwargs)
        assert removed == comment_liked
        assert comment.likes_num == (
            likes_num - 1 if comment_liked else likes_num)
        assert not comment.likes.all()
    else:
        assert not remove_like(data, **default_kwargs)
