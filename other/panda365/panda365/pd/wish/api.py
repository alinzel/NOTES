from flask import Blueprint
from marshmallow.fields import Integer
from sqlalchemy import and_
from sqlalchemy.orm import contains_eager, subqueryload
from sqlalchemy_utils import sort_query
from pd.api import abort_json
from pd.api.io import io_annotated
from pd.api.fields import Enum
from pd.auth.jwt import auth_optional, auth_required, current_user_data
from pd.constants import Country
from pd.facebook.api.comments import (
    CreateCommentSchema, _generic_comment_create, _generic_comments_list,
)
from pd.facebook.schema import CommentSchema
from pd.sqla import db
from .models import Vote, Wish, WishPrice
from .schema import VoteSchema, WishSchema, WishStatus


api = Blueprint('wish_api', __name__, url_prefix='/v1')


@api.route('/wishes/')
@auth_optional
@io_annotated
def wishes_list(country: Enum(Country)) -> WishSchema(many=True):
    """
    投票中的Wish列表
    """
    q = Wish.query.join(
        WishPrice
    ).filter(
        Wish.status == WishStatus.voting,
    ).options(
        subqueryload('media'),
        contains_eager('prices')
    )
    if country:
        q = q.filter(
            WishPrice.country == country
        )
    if current_user_data:
        q = q.outerjoin(
            Vote, and_(
                Vote.user_id == current_user_data['id'],
                Vote.wish_id == Wish.id,
            )
        ).options(
            contains_eager(Wish.my_vote)
        )
    return sort_query(q, '-created_at')


@api.route('/wishes/voted/')
@auth_required
@io_annotated
def voted_wishes_list() -> WishSchema(many=True):
    """
    我的投票wish列表
    """
    q = Wish.query.join(
        Vote, and_(
            Vote.user_id == current_user_data['id'],
            Vote.wish_id == Wish.id,
        )
    ).options(
        subqueryload('media'),
        contains_eager(Wish.my_vote),
    )
    return sort_query(q, '-created_at')


@api.route('/wishes/<int:wish_id>/votes/', methods=('POST',))
@auth_required
@io_annotated
def vote_create(wish_id: Integer(location='view_args')) -> VoteSchema():
    """
    对wish投票.

    可能的错误:

    - 409:
        + 用户对当前wish在最近1天内已经投过票
        + wish已达到投票目标
        + wish状态不是voting
    - 404: 指定的wish不存在

    """
    wish = Wish.query.get_or_404_json(wish_id)
    if not wish.can_vote:
        abort_json(409, 'wish is finished: target reached or cancelled')
    vote = Vote.vote(wish_id=wish_id, user_id=current_user_data['id'])
    if not vote:
        abort_json(409, 'you can only vote once per wish each day')
    db.session.commit()
    return vote


@api.route('/wishes/<int:id>/comments/', methods=('POST',))
@auth_required
@io_annotated
def comment_create(**data: CreateCommentSchema()) -> CommentSchema():
    """
    **已过时** 请使用`facebook.comment_create`接口

    为wish创建评论
    """
    data.update({
        'parent_type': 'Wish',
        'parent_id': data['id'],
    })
    return _generic_comment_create(data)


@api.route('/wishes/<int:wish_id>/comments/')
@io_annotated
def comments_list(wish_id) -> CommentSchema(many=True):
    """
    **已过时** 请使用`facebook.comments_list`接口

    获取wish的评论
    """
    return _generic_comments_list('Wish', wish_id)
