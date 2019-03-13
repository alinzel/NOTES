import hmac
from flask import request, current_app
from marshmallow import fields, validates, ValidationError
from pd.api.fields import Enum, ProductInfo
from pd.api.schema import Schema, ModelSchema as BaseModelSchema
from pd.vendor.schema import VendorLinkSchema
from .fields import Gid
from .models import Comment, Post, User, Like, MediaType


class FBUpdateEntrySchema(Schema):
    id = fields.String()
    changed_fields = fields.List(fields.String)
    changes = fields.List(fields.Dict)
    time = fields.Int()


class FBUpdateSchema(Schema):
    object = fields.String()
    entry = fields.Nested(FBUpdateEntrySchema(many=True))
    signature = fields.String(load_from='X-hub-signature')

    @validates('signature')
    def validate_signature(self, value):
        digest = 'sha1=' + hmac.new(
            key=current_app.config['FACEBOOK_APP_SECRET'].encode(),
            msg=request.data,
            digestmod='sha1'
        ).hexdigest()
        if not hmac.compare_digest(digest, value):
            raise ValidationError('signature mismatch')


class ModelSchema(BaseModelSchema):
    gid = Gid(description='global id')


class UserSchema(ModelSchema):

    class Meta:
        model = User
        fields = ('id', 'gid', 'fb_id', 'name', 'icon_url')


class PostSchema(ModelSchema):

    class Meta:
        model = Post
        fields = (
            'id', 'gid', 'fb_id',
            'created_at', 'likes_num', 'comments_num', 'user',
            'message', 'photo_urls', 'vendor_links', 'media_type',
            'is_shopping', 'price', 'currency', 'sale_on',
            'info',
        )

    user = fields.Nested(UserSchema)
    vendor_links = fields.Nested(VendorLinkSchema, many=True)
    media_type = Enum(MediaType)
    info = ProductInfo()


_reply_fields = [
    'id', 'gid', 'fb_id', 'parent_gid',
    'created_at', 'user', 'message', 'photo_url',
    'comments_num', 'likes_num',
]


class ReplySchema(ModelSchema):

    class Meta:
        model = Comment
        fields = _reply_fields

    user = fields.Nested(UserSchema)


class CommentSchema(ReplySchema):

    class Meta:
        model = Comment
        fields = _reply_fields + [
            'replies'
        ]

    replies = fields.Nested(ReplySchema, many=True)


class LikeSchema(ModelSchema):

    class Meta:
        model = Like
        fields = (
            'id',
            'parent_gid',
        )

    parent_gid = Gid()
