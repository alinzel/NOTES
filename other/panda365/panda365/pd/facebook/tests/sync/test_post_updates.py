import arrow
import pytest
from unittest.mock import patch
from pd.facebook.models import Comment, Post, MediaType
from pd.facebook.signal_handlers import add_post, edit_post, remove_post
from pd.facebook.factory import UserFactory, PostFactory, PostPhotoFactory


pytestmark = pytest.mark.db


@pytest.fixture
def mock_sync_fb_file():
    with patch('pd.facebook.signal_handlers.posts.sync_fb_static_file') as m:
        m.return_value = 'https://uuid_400_600.jpg'
        yield m


def _create_post(**kwargs):
    kwargs.setdefault('photos', [PostPhotoFactory.build()])
    return PostFactory(**kwargs)


# it doesn't matter if the user exists; it is created if not
@pytest.mark.parametrize('user_exists', [True, False])
def test_create_post_without_photo(user_exists, default_kwargs):
    data = {
        "item": "status",
        "sender_name": "Panda365",
        "sender_id": 286247441793403,
        "post_id": "286247441793403_288731331545014",
        "verb": "add",
        "published": 1,
        "created_time": 1489996742,
        "message": "test post without a photo"
    }
    if user_exists:
        UserFactory(fb_id=str(data['sender_id']))

    post = add_post(data, **default_kwargs)
    assert post.fb_id == '286247441793403_288731331545014'
    assert post.fb_page_id == 'page_id'
    assert post.created_at.timestamp == 1489996742
    assert post.message == "test post without a photo"
    # visibility fields
    assert not post.is_active  # stop showing fb posts by default
    assert post.publish_at == arrow.get(data['created_time'])
    assert not post.photos
    assert post.user.name == 'Panda365'
    assert post.user.fb_id == '286247441793403'


def test_create_post_conflict(default_kwargs):
    # post with the fb_id already exists
    data = {
        "item": "status",
        "sender_name": "Panda365",
        "sender_id": 286247441793403,
        "post_id": "286247441793403_288731331545014",
        "verb": "add",
        "published": 1,
        "created_time": 1489996742,
        "message": "test post without a photo"
    }
    existing_post = _create_post(
        fb_id=data['post_id'], message=data['message'])
    post = add_post(data, **default_kwargs)
    assert not post
    assert Post.fb_query(data['post_id']).one() == existing_post


def test_create_post_with_one_photo(default_kwargs, mock_sync_fb_file):
    data = {
        "photo_id": 288733964878084,
        "item": "photo",
        "sender_name": "Panda365",
        "sender_id": 286247441793403,
        "post_id": "286247441793403_288733964878084",
        "verb": "add",
        "link": "http://scontent.xx.fbcdn.net/v/t1.0-9/17352225_288733964878084_2671670063696108827_n.jpg?oh=18b3c9fd292434aee93b262c1cd9e6bd&oe=59619394",  # noqa
        "published": 1,
        "message": "test page with one photo"
    }
    post = add_post(data, **default_kwargs)
    assert len(post.photo_urls) == 1
    assert post.media_type == MediaType.photo
    assert mock_sync_fb_file.called
    assert mock_sync_fb_file.call_args[0] == (data['link'],)


def test_create_post_with_multiple_photos(default_kwargs, mock_sync_fb_file):
    data = {
         "item": "status",
         "sender_name": "Panda365",
         "post_id": "286247441793403_288734468211367",
         "sender_id": 286247441793403,
         "photos": [
             "http://scontent.xx.fbcdn.net/v/t1.0-9/17156300_288734411544706_543646130214677003_n.jpg?oh=6cb1f0c16989e58cf2a73523e7a26b1b&oe=5963B4B9",  # noqa
             "http://scontent.xx.fbcdn.net/v/t1.0-9/17352020_288734434878037_1074731854245887317_n.jpg?oh=80a4898ea862bac2e0b1a5fdd55afc1b&oe=596787CF",  # noqa
         ],
         "verb": "add",
         "published": 1,
         "created_time": 1489997336,
         "message": "test post with multiple photos"
    }
    post = add_post(data, **default_kwargs)
    assert post
    assert post.media_type == MediaType.photo
    assert data['photos'] == [  # pragma: no cover
        call[0][0] for call in mock_sync_fb_file.call_args_list]


@pytest.mark.parametrize('post_exists', [True, False])
def test_edit_post_message(db_session, post_exists, default_kwargs):
    data = {
        "item": "status",
        "sender_name": "Panda365",
        "sender_id": 286247441793403,
        "post_id": "286247441793403_288731331545014",
        "verb": "edited",
        "published": 1,
        "created_time": 1489996742,
        "message": "test post without a"
    }
    if post_exists:
        post = _create_post(fb_id=data['post_id'], message='1')
        assert edit_post(data, **default_kwargs)
        db_session.refresh(post)
        assert post.message == 'test post without a'
        assert Post.fb_query(data['post_id']).count() == 1
    else:
        assert not edit_post(data, **default_kwargs)
        assert not Post.fb_query(data['post_id']).first()


@pytest.mark.parametrize('post_exists', [True, False])
def test_delete_post(db_session, post_exists, default_kwargs):
    # 不管post是否包含照片，参数都是如此
    data = {
        "verb": "remove",
        "item": "post",
        "sender_name": "Panda365",
        "sender_id": 286247441793403,
        "post_id": "286247441793403_288734468211367",
        "recipient_id": 286247441793403,
        "created_time": 1489998234
    }
    if post_exists:
        post = _create_post(fb_id=data['post_id'])
        post.add_comment(fb_id='comment', user=UserFactory())
        assert remove_post(data, **default_kwargs)
        # comment related to the post should be deleted
        db_session.expire_all()
        assert not Comment.fb_query('comment').first()
    else:
        assert not remove_post(data, **default_kwargs)
        assert not Post.fb_query(data['post_id']).first()
