import base64
from datetime import date
from unittest.mock import patch
import pytest
from pd.vendor.factory import VendorLinkFactory
from .. factory import (
    UserFactory, PostFactory, PostPhotoFactory, CommentFactory, LikeFactory,
)
from ..models import Base, Post, Comment, Like, User, MediaType


pytestmark = pytest.mark.db


@pytest.fixture
def user():
    return UserFactory()


def test_models(db_session, user):
    # post
    photo = PostPhotoFactory.build()
    post = PostFactory(photos=[photo])
    post.photo_urls == [photo.url]

    # comment
    comment = CommentFactory(user=user, parent=post)
    assert post.comments.all() == [comment]
    assert not comment.is_reply

    # reply
    reply = CommentFactory(user=user, parent=comment)
    assert reply.is_reply
    assert comment.comments.all() == [reply]

    # likes
    post_like = LikeFactory(parent=post, user=user)
    comment_like = LikeFactory(parent=comment, user=user)
    Like.query.filter(Like.parent.is_type(Post)).all() == [post_like]
    Like.query.filter(Like.parent.is_type(Comment)).all() == [comment_like]

    # can delete post with photos
    db_session.delete(post)
    db_session.commit()


@pytest.mark.parametrize('is_s3_url', [True, False])
def test_photo_delete_event(app, db_session, is_s3_url):
    if is_s3_url:
        url = '//{}/test.jpg'.format(app.config['S3_BUCKET'])
    else:
        url = 'http://test.jpg'

    post = PostFactory()
    photo = PostPhotoFactory(url=url, post=post)
    with patch('pd.facebook.models.entities.s3ext') as s3ext:
        db_session.delete(photo)
        db_session.commit()
        assert s3ext.store.delete_file.called == is_s3_url


def test_try_insert(user):
    fb_id = 'post_id'
    data = dict(fb_id=fb_id, fb_page_id='123')
    post = Post.try_insert(**data)
    assert post
    assert Post.fb_query(fb_id).first() == post
    assert not Post.try_insert(**data)


@pytest.mark.parametrize('comment_exists', [True, False])
def test_post_add_comment(user, comment_exists):
    post, post2 = PostFactory.create_batch(2)
    comments_num = post.comments_num
    comments_num2 = post2.comments_num
    if comment_exists:
        comment = CommentFactory(parent=post)
        assert not post.add_comment(fb_id=comment.fb_id, user=user)
        assert post.comments_num == comments_num
    else:
        assert post.add_comment(fb_id='commentid', user=user)
        assert post.comments_num == comments_num + 1
    # post2 should not be affacted
    assert comments_num2 == post2.comments_num


@pytest.mark.parametrize('comment_exists', [True, False])
def test_post_remove_comment(user, comment_exists):
    post, post2 = PostFactory.create_batch(2)
    comments_num = post.comments_num
    comments_num2 = post2.comments_num
    if comment_exists:
        comment = CommentFactory(parent=post)
        assert post.remove_comment(fb_id=comment.fb_id)
        assert post.comments_num == comments_num - 1
    else:
        assert not post.remove_comment(fb_id='commentid')
        assert post.comments_num == comments_num
    # post2 should not be affacted
    assert comments_num2 == post2.comments_num


def test_post_media_type(db_session):
    post = PostFactory.build()
    photo = PostPhotoFactory.build()
    db_session.add(post)
    db_session.add(photo)
    for photo_url, expected_type in (
        ('a.jpg', MediaType.photo),
        ('a.jpeg', MediaType.photo),
        ('a.png', MediaType.photo),
        ('a.gif', MediaType.gif),
        ('a.mp4', MediaType.video),
    ):
        photo.url = photo_url
        photo.post = post
        db_session.commit()
        assert post.media_type == expected_type


def test_post_is_shopping(db_session):
    post = PostFactory()
    assert not post.is_shopping
    post.sale_on = date(2017, 1, 1)
    db_session.commit()
    assert post.is_shopping
    VendorLinkFactory(post=post)
    assert post.is_shopping


def test_gid(user):
    assert Base.decode_gid(user.gid) == (User, user.id)


@pytest.mark.parametrize('gid', [
    '',
    'blah',
    base64.b64encode(b'InvalidModel:123').decode(),
])
def test_decode_gid_errors(gid):
    assert not Base.decode_gid(gid)
