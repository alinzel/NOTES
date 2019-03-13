from itertools import groupby
from marshmallow import fields
from sqlalchemy import and_, or_
from pd.api import abort_json, io_annotated
from pd.auth.jwt import auth_required, current_user_data
from pd.sqla import db
from ..models import Post, Comment, Like
from ..schema import LikeSchema
from ..fields import Gid
from . import api


def _create_like(parent_cls, id):
    parent = parent_cls.query.get_or_404_json(id)
    like = parent.add_like(user_id=current_user_data['id'])
    db.session.commit()
    if not like:
        like = Like.query.filter(
            Like.user_id == current_user_data['id'],
            Like.parent.is_type(parent_cls),
            Like.parent_id == id,
        ).first()
    return like


_like_schema = LikeSchema()


@api.route('/posts/<int:id>/likes/', methods=('POST',))
@auth_required
@io_annotated
def post_likes_create(id) -> _like_schema:
    """
    对post进行like
    """
    return _create_like(Post, id)


@api.route('/comments/<int:id>/likes/', methods=('POST',))
@auth_required
@io_annotated
def comment_likes_create(id) -> _like_schema:
    """
    对post进行like
    """
    return _create_like(Comment, id)


@api.route('/likes/')
@auth_required
@io_annotated
def likes_list(
        parent_gids: fields.List(
            Gid(required=True), locations=('query', 'json'))
) -> LikeSchema(many=True):
    """
    根据global id获取like. 参数`parent_gids`可以通过query或json传递.

    通过query传递时，可使用多次来获取多个item的like:

        GET /v1/likes/?parent_gids=UG9zdHwyMjg4&parent_gids=Q29tbWVudHwxNTk4

    json:

        GET /v1/likes/

        {
            "parent_gids": ["UG9zdHwyMjg4", "Q29tbWVudHwxNTk4"]
        }

    """
    q = Like.query.filter(Like.user_id == current_user_data['id'])
    if parent_gids:
        gids = sorted(
            (parent_type.__name__, id) for parent_type, id in parent_gids
            if parent_type in (Comment, Post))
        valid_filters = [
            and_(
                Like.parent_type == parent_type,
                Like.parent_id.in_(set(id for _, id in group))
            ) for parent_type, group in groupby(gids, key=lambda r: r[0])]
        if valid_filters:
            q = q.filter(or_(*valid_filters))
        else:
            return []
    return q


@api.route('/likes/<int:id>', methods=('DELETE',))
@auth_required
@io_annotated
def likes_delete(id: fields.Int(required=True, location='view_args')):
    like = Like.query.filter(
        Like.user_id == current_user_data['id'],
        Like.id == id,
    ).first()
    if not like:
        abort_json(404, 'Like {} not found'.format(id))
    like.remove()
    db.session.commit()
    return '', 204
