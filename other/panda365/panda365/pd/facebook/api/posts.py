from marshmallow.fields import List
from sqlalchemy import or_
from sqlalchemy.orm import joinedload, subqueryload
from sqlalchemy_utils import sort_query
from pd.api import io_annotated
from pd.api.fields import Enum
from pd.auth.jwt import auth_required, current_user_data
from pd.bookmark.models import Bookmark
from ..models import Post, Like, User, Country, MediaType
from ..schema import PostSchema
from . import api


def _get_posts(q, media_type=None):
    if media_type:
        q = q.filter(Post.media_type.in_(media_type))
    return sort_query(q.filter(
        Post.is_visible
    ).options(
        subqueryload(Post.user),
        subqueryload(Post.photos),
        joinedload(Post.vendor_links).joinedload('vendor'),
    ), '-updated_at')


_media_type_spec = List(
    Enum(MediaType),
    description='按media_type筛选posts. 可多次使用来指定多个type, 例如'
                '`GET /v1/posts/?media_type=gif&media_type=photo`',
    location='query',
)


@api.route('/posts/')
@io_annotated
def posts_list(media_type: _media_type_spec) -> PostSchema(many=True):
    '''
    posts列表接口
    '''
    return _get_posts(
        Post.query.filter(Post.is_shopping.is_(False)), media_type
    )


@api.route('/posts/liked/')
@auth_required
@io_annotated
def liked_posts_list() -> PostSchema(many=True):
    '''
    Liked posts列表. 需要用户登录
    '''
    return _get_posts(
        Post.query.join(
            Post.likes,
        ).join(
            User, Like.user_id == User.id
        ).filter(
            User.id == current_user_data['id'],
        )
    )


@api.route('/posts/shopping/')
@io_annotated
def shopping_posts_list(
    media_type: _media_type_spec, country: Enum(Country)
) -> PostSchema(many=True):
    '''
    Shopping posts列表
    '''
    q = Post.query.filter(Post.is_shopping)
    if country:
        q = q.filter(or_(Post.country == country, Post.country.is_(None)))
    return _get_posts(q, media_type)


@api.route('/posts/bookmarked/')
@auth_required
@io_annotated
def bookmarked_posts_list() -> PostSchema(many=True):
    '''
    收藏posts列表
    '''
    return _get_posts(
        Post.query.join(Post.bookmarks).filter(
            Bookmark.user_id == current_user_data['id']
        )
    )
