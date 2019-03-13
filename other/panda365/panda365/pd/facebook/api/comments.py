from itertools import groupby

from flask import current_app
from marshmallow import (
    fields, validate, validates, validates_schema, Schema, ValidationError,
)
from sqlalchemy import func, desc
from sqlalchemy.orm import joinedload, subqueryload
from pd.api import io_annotated
from pd.api.fields import DataURL
from pd.auth.jwt import auth_required, current_user_data
from pd.ext import s3ext
from pd.sqla import db
from . import api, reverse_created_at
from ..models import Post, Comment
from ..schema import CommentSchema, ReplySchema


# list comments

def fetch_comment_replies(comments):
    if comments:
        replies_group_q = db.session.query(
            Comment,
            func.row_number().over(
                partition_by=Comment.parent_id,
                order_by=desc(Comment.created_at),
            ).label('row_num'),
        ).filter(
            Comment.parent.is_type(Comment),  # only replies
            Comment.parent_id.in_(c.id for c in comments),
        ).subquery()
        replies = Comment.query.select_entity_from(replies_group_q).filter(
            replies_group_q.c.row_num <= current_app.config['API_PER_PAGE'],
        ).options(
            subqueryload(Comment.user),
        )
        cid_to_replies = {
            cid: list(g) for cid, g in groupby(replies, lambda c: c.parent_id)}
        for c in comments:
            c.replies = cid_to_replies.get(c.id, [])


def _generic_comments_list(parent_type, parent_id):
    pagination = reverse_created_at(Comment.query.filter_by(
        parent_type=parent_type,
        parent_id=parent_id,
        is_active=True,
    ).options(
        joinedload(Comment.user)
    )).paginate()
    if parent_type != 'Comment':  # we're fetching comments, not replies
        # load first pages of replies for the comments
        fetch_comment_replies(pagination.items)
    return pagination


@api.route('/posts/<int:id>/comments/')
@io_annotated
def post_comments_list(id) -> CommentSchema(many=True):
    '''
    返回指定post的comments
    '''
    return _generic_comments_list('Post', id)


@api.route('/comments/<int:id>/replies/')
@io_annotated
def comment_replies_list(id) -> ReplySchema(many=True):
    '''
    返回指定comment的回复
    '''
    return _generic_comments_list('Comment', id)


# create comments
class CreateCommentSchema(Schema):
    id = fields.Int(required=True, location='view_args')
    message = fields.Str(
        validate=[validate.Length(min=1, max=512)],
        location='json', missing=None)
    photo = DataURL(location='json')

    @validates_schema
    def validate_schema(self, data):
        if not data.get('message') and not data.get('photo'):
            raise ValidationError('message and photo cannot both be empty')


def _create_comment(parent_cls, data):
    """
    Post and Comment handle `comments_num` differently than Wish and Product.
    That's why we have `_create_comment` and `_generic_comment_create`.
    Once Post and Comment are completely deprecated, clean up this code.
    """
    parent = parent_cls.query.get_or_404_json(data['id'])
    comment = parent.add_comment(
        message=data.get('message'),
        user_id=current_user_data['id'],
    )
    if data.get('photo'):
        comment.photo_url = s3ext.save_file(
            data['photo'], 'images/comments/{}'.format(comment.id))
    db.session.commit()
    return comment


@api.route('/posts/<int:id>/comments/', methods=('POST',))
@auth_required
@io_annotated
def post_comments_create(**data: CreateCommentSchema()) -> CommentSchema():
    """
    对post进行评论
    """
    return _create_comment(Post, data)


@api.route('/comments/<int:id>/replies/', methods=('POST',))
@auth_required
@io_annotated
def comment_replies_create(**data: CreateCommentSchema()) -> CommentSchema():
    """
    对评论进行回复
    """
    return _create_comment(Comment, data)


class GenericCreateCommentSchema(Schema):
    parent_id = fields.Int(required=True)
    parent_type = fields.Str(required=True)
    message = fields.Str(
        validate=[validate.Length(min=1, max=512)], missing=None)
    photo = DataURL()

    @validates_schema
    def validate_schema(self, data):
        if not data.get('message') and not data.get('photo'):
            raise ValidationError('message and photo cannot both be empty')

    @validates('parent_type')
    def validate_parent_type(self, data):
        if data not in db.Model._decl_class_registry:
            raise ValidationError('this type is not defined')


def _generic_comment_create(data):
    parent_cls = db.Model._decl_class_registry[data['parent_type']]
    parent = parent_cls.query.get_or_404_json(data['parent_id'])
    comment = Comment(
        parent=parent,
        user_id=current_user_data['id'],
        message=data.get('message'),
    )
    db.session.add(comment)
    db.session.flush()  # get id
    if data.get('photo'):
        comment.photo_url = s3ext.save_file(
            data['photo'], 'images/comments/{}'.format(comment.id))
    db.session.commit()
    return comment


@api.route('/comments/', methods=('POST',))
@auth_required
@io_annotated
def comment_create(**data: GenericCreateCommentSchema()) -> CommentSchema():
    """
    创建评论通用接口
    """
    return _generic_comment_create(data)


@api.route('/comments/')
@io_annotated
def comments_list(
    parent_type: fields.Str(required=True, location='query'),
    parent_id: fields.Int(required=True, location='query'),
) -> CommentSchema(many=True):
    return _generic_comments_list(parent_type, parent_id)
