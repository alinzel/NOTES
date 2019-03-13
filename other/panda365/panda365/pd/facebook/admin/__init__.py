from sqlalchemy import func
from pd.admin.base import ModelView
from pd.admin.format import (
    format_imgs, format_links, model_detail_link, model_list_link,
)
from .posts import (
    AllPostAdmin, PostAdmin, PreSaleProductAdmin, OnSaleProductAdmin,
)


__all__ = [
    'AllPostAdmin',
    'PostAdmin',
    'PreSaleProductAdmin',
    'OnSaleProductAdmin',
    'ReplyAdmin',
    'CommentAdmin',
    'WishCommentAdmin',
    'LikeAdmin',
    'PostPhotoAdmin',
]


class ReplyAdmin(ModelView):
    can_create = False
    can_delete = True
    column_list = (
        'id',
        'is_from_fb',
        'reply_to',
        'message',
        'user',
        'photo',
    )
    column_filters = (
        'fb_id',
        'parent_id',
    )
    form_columns = (
        'user_id',
        'parent_id',
        'parent_type',
        'created_at',
        'fb_id',
        'comments_num',
        'likes_num',
        'message',
        'photo_url'
    )
    parent_type = 'Comment'

    def format_photo(self, ctx, model, name):
        if model.photo_url:
            return format_imgs(model.photo_url)

    def format_reply_to(self, ctx, model, name):
        return model_detail_link(model.parent_type, model.parent_id)

    column_formatters = dict(
        photo=format_photo,
        reply_to=format_reply_to,
    )

    def _q_filter(self):
        return self.model.parent_type == self.parent_type

    def get_query(self):
        return self.session.query(self.model).filter(self._q_filter())

    def get_count_query(self):
        return self.session.query(func.count('*')).select_from(
            self.model).filter(self._q_filter())

    def is_visible(self):
        return self.has_roles('dev')


class CommentAdmin(ReplyAdmin):
    parent_type = 'Post'
    can_delete = True
    column_default_sort = ('created_at', True)
    column_list = (
        'id',
        'is_from_fb',
        'user',
        'reply_to',
        'related',
        'message',
        'photo',
    )

    def format_related(self, ctx, model, name):
        return format_links(
            model_list_link(
                'Reply', 'replies',
                flt_parent_id_equals=model.id,
            ),
            model_list_link(
                'Like',
                flt_parent_id_equals=model.id,
                flt_parent_type_equals='Comment',
            )
        )

    column_formatters = dict(
        related=format_related,
        **ReplyAdmin.column_formatters
    )


class WishCommentAdmin(CommentAdmin):
    parent_type = 'Wish'


class ProductCommentAdmin(CommentAdmin):
    parent_type = 'Product'


class LikeAdmin(ModelView):
    can_create = False
    column_list = (
        'id',
        'is_from_fb',
        'reply_to',
        'user',
    )
    column_filters = (
        'fb_id',
        'parent_id',
        'parent_type',
    )

    def format_reply_to(self, ctx, model, name):
        return model_detail_link(model.parent_type, model.parent_id)

    column_formatters = dict(
        reply_to=format_reply_to,
    )

    def is_visible(self):
        return self.has_roles('dev')


class PostPhotoAdmin(ModelView):
    can_create = False
    column_list = (
        'id',
        'post_id',
        'url',
    )
    column_default_sort = ('id', True)

    def format_post_id(self, ctx, model, name):
        return model_detail_link('Post', model.post_id)

    def format_url(self, ctx, model, name):
        return format_imgs(model.url)

    column_formatters = dict(
        post_id=format_post_id,
        url=format_url,
    )

    def is_visible(self):
        return self.has_roles('dev')
