from enum import Enum
import arrow
from flask import current_app
import sqlalchemy_utils as su
from sqlalchemy import func, event, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from pd.constants import Country
from pd.ext import s3ext
from pd.sqla import (
    db, ignore_integrity_error, translation_hybrid,
)
from .base import Base, ActionParentMixin
from .users import UserCreatedMixin


class _CommentParentMixin(ActionParentMixin):
    comments_num = db.Column(db.Integer, default=0, server_default='0')

    def add_comment(self, **kwargs):
        return self.add_action(Comment, **kwargs)

    def remove_comment(self, **kwargs):
        return self.remove_action(Comment, **kwargs)

    @declared_attr
    def comments(cls):
        parent_id = 'Comment.parent_id'
        parent_type = 'Comment.parent_type'
        if cls.__name__ == 'Comment':
            # Comment.comments: we're self-joining
            # we need to mark the remote side of the join
            parent_id = 'remote({})'.format(parent_id)
            parent_type = 'remote({})'.format(parent_type)
        return db.relationship(
            'Comment',
            primaryjoin=(
                "and_({parent_id} == foreign({cls}.id), {parent_type} == '{cls}')"  # noqa
            ).format(
                parent_id=parent_id, parent_type=parent_type, cls=cls.__name__
            ),
            uselist=True,
            single_parent=True,
            cascade='all, delete-orphan',
            lazy='dynamic',
        )


class _LikeParentMixin(ActionParentMixin):
    likes_num = db.Column(db.Integer, default=0, server_default='0')

    _uq_user_parent_pattern = 'uq_like_user_parent'

    def add_like(self, **kwargs):
        with ignore_integrity_error(self._uq_user_parent_pattern):
            return self.add_action(Like, **kwargs)

    def remove_like(self, **kwargs):
        return self.remove_action(Like, **kwargs)

    @declared_attr
    def likes(cls):
        return db.relationship(
            'Like',
            primaryjoin=(
                "and_(Like.parent_id == foreign({cls}.id), "
                "Like.parent_type == '{cls}')"
            ).format(cls=cls.__name__),
            uselist=True,
            single_parent=True,
            cascade='all, delete-orphan',
            lazy='dynamic',
        )


class Like(UserCreatedMixin, Base):
    parent_id = db.Column(db.Integer, nullable=False)
    parent_type = db.Column(db.Text, nullable=False)
    parent = su.generic_relationship(parent_type, parent_id)
    user = db.relationship(
        'User',
        backref=db.backref(
            'likes', cascade='all, delete-orphan', passive_deletes=True),
    )

    __table_args__ = (
        UniqueConstraint(
            'user_id', 'parent_id', 'parent_type',
            name='uq_like_user_parent',
        ),
    )

    @property
    def parent_gid(self):
        return self.encode_gid(self.parent_type, self.parent_id)

    def remove(self):
        self.parent.likes_num = self.parent.__table__.c.likes_num - 1
        db.session.delete(self)


class PostPhoto(UserCreatedMixin, db.Model):
    url = db.Column(db.Text, nullable=False)
    post_id = db.Column(
        db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'),
        nullable=False,
    )
    post = db.relationship(
        'Post',
        backref=db.backref(
            'photos', cascade='all, delete-orphan', passive_deletes=True,
            order_by='PostPhoto.id',
        )
    )

    user = db.relationship(
        'User',
        backref=db.backref(
            'post_photos', cascade='all, delete-orphan', passive_deletes=True)
    )


@event.listens_for(PostPhoto, 'before_delete')
def delete_photo_from_s3(mapper, connection, photo):
    s3_url_prefix = '//{}/'.format(current_app.config['S3_BUCKET'])
    if photo.url and photo.url.startswith(s3_url_prefix):
        path = photo.url.replace(s3_url_prefix, '')
        s3ext.store.delete_file(path)


class MediaType(Enum):
    post = 1
    photo = 2
    gif = 3
    video = 4


class Post(UserCreatedMixin, _CommentParentMixin, _LikeParentMixin, Base):
    updated_at = db.Column(su.ArrowType, default=arrow.utcnow)
    fb_page_id = db.Column(db.Text)
    message_translations = db.Column(JSONB)
    message = translation_hybrid(message_translations)
    # 商品信息
    info_translations = db.Column(JSONB)
    info = translation_hybrid(info_translations)

    media_type = db.Column(su.ChoiceType(MediaType, impl=db.SmallInteger()))

    user = db.relationship(
        'User',
        backref=db.backref(
            'posts', cascade='all, delete-orphan', passive_deletes=True),
        lazy='joined',
    )
    is_active = db.Column(db.Boolean, default=False, nullable=False)
    # is_shopping means the post has at least 1 vendor_link or sale_on
    # is set. Its value is automatically set by orm events, see
    # `set_is_shopping` below
    is_shopping = db.Column(db.Boolean, default=False, server_default='false')
    publish_at = db.Column(su.ArrowType, default=arrow.utcnow)
    # product info
    price = db.Column(db.Float)
    currency = db.Column(su.CurrencyType)
    sale_on = db.Column(db.Date)
    country = db.Column(su.ChoiceType(Country, impl=db.Text()))

    @hybrid_property
    def is_visible(self):
        return (
            self.is_active == True and   # noqa
            self.publish_at <= arrow.utcnow()
        )

    @is_visible.expression
    def is_visible(cls):
        return (
            cls.is_active.is_(True) &  # noqa
            (cls.publish_at <= func.timezone('utc', func.now()))
        )

    @property
    def photo_urls(self):
        return [photo.url for photo in self.photos]

    @staticmethod
    def caculate_media_type(post):
        if not post.photos:
            return MediaType.post
        url = post.photos[0].url
        if url.endswith('.gif'):
            return MediaType.gif
        elif url.endswith('.mp4'):
            return MediaType.video
        else:
            return MediaType.photo


def set_caculated_attrs(mapper, connection, target):
    target.is_shopping = bool(target.sale_on or target.vendor_links)
    # the following does not guarantee that a post's media type is always
    # set correctly; for example, if a photo is inserted on it's own, there's
    # no way that this handler will fire.
    # However, since posts and their photos are usually handled by admin
    # and the facebook sync handlers, they all involve using the post object.
    # This covers these use cases.
    target.media_type = Post.caculate_media_type(target)


event.listens_for(Post, 'before_update')(set_caculated_attrs)
event.listens_for(Post, 'before_insert')(set_caculated_attrs)


class Comment(UserCreatedMixin, _CommentParentMixin, _LikeParentMixin, Base):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text)
    photo_url = db.Column(db.Text)

    parent_id = db.Column(db.Integer, nullable=False)
    parent_type = db.Column(db.Text, nullable=False)
    parent = su.generic_relationship(parent_type, parent_id)
    is_active = db.Column(db.Boolean, default=True, server_default='true')

    user = db.relationship(
        'User',
        backref=db.backref(
            'comments', cascade='all, delete-orphan', passive_deletes=True),
    )

    @property
    def parent_gid(self):
        return self.encode_gid(self.parent_type, self.parent_id)

    @hybrid_property
    def is_reply(self):
        return self.parent_type == 'Comment'
