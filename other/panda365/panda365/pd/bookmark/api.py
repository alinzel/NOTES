from flask import Blueprint
from marshmallow import fields
from sqlalchemy.exc import IntegrityError
from pd.api import abort_json, io_annotated
from pd.auth.jwt import auth_required, current_user_data
from pd.sqla import db
from .models import Bookmark
from .schema import BookmarkSchema


api = Blueprint('bookmark', __name__, url_prefix='/v1')


@api.route('/posts/<id>/bookmarks/', methods=('POST',))
@auth_required
@io_annotated
def bookmarks_create(id: fields.Int(location='view_args')) -> BookmarkSchema():
    """
    收藏post.
    """
    kwargs = dict(post_id=id, user_id=current_user_data['id'])
    b = Bookmark(**kwargs)
    try:
        db.session.add(b)
        db.session.commit()
    except IntegrityError as e:
        if Bookmark.UQ_NAME in str(e):
            # already bookmarked
            db.session.rollback()
            return Bookmark.query.filter_by(**kwargs).first()
        else:
            abort_json(404, 'post({}) does not exist'.format(id))
    return b


@api.route('/bookmarks/')
@auth_required
@io_annotated
def bookmarks_list(
        post_ids: fields.List(fields.Int(), locations=('query', 'json'))
) -> BookmarkSchema(many=True):
    """
    收藏列表。

    可根据post_id进行过滤，可通过query或json传参，同
    <a href="#facebook.likes_list">facebook.likes_list</a>.
    """
    q = Bookmark.query.filter_by(user_id=current_user_data['id'])
    if post_ids:
        q = q.filter(Bookmark.post_id.in_(set(post_ids)))
    return q


@api.route('/bookmarks/<id>', methods=('DELETE',))
@auth_required
@io_annotated
def bookmarks_delete(id: fields.Int(location='view_args')):
    """
    取消收藏
    """
    deleted = Bookmark.query.filter_by(
        id=id,
        user_id=current_user_data['id'],
    ).delete()
    if deleted:
        db.session.commit()
        return '', 204
    abort_json(404, 'bookmark not found')
