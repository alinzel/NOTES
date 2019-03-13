import arrow
from flask import current_app, flash, Markup
from flask_admin.helpers import get_form_data
from flask_admin.model.form import InlineFormAdmin
from werkzeug.datastructures import FileStorage
from wtforms.validators import DataRequired
from sqlalchemy.orm import subqueryload
from pd.admin.base import ModelView
from pd.admin.fields import (
    S3ImageUploadField, HybridTranslationField, ProductInfoTranslationField,
)
from pd.admin.format import (
    format_imgs, format_links, model_list_link, trans_hybrid_formatter,
    trans_hybrid_product_info_formatter,
)
from pd.admin.utils import create_cover_for_gif
from pd.facebook.models import PostPhoto, Post, User
from pd.vendor.models import VendorLink


class PostPhotoInlineForm(InlineFormAdmin):
    form_columns = ('id', 'url')
    form_label = 'Photos'
    form_overrides = dict(
        url=S3ImageUploadField,
    )
    form_args = dict(
        url=dict(s3_directory='images/posts'),
    )


class _BasePostAdmin(ModelView):
    list_template = 'admin/post_list.html'
    create_template = 'admin/post_create.html'
    edit_template = 'admin/post_edit.html'
    inline_models = (PostPhotoInlineForm(PostPhoto),)
    can_create = True
    column_sortable_list = ('updated_at', 'comments_num', 'likes_num')
    column_default_sort = ('updated_at', True)
    form_overrides = dict(
        message_translations=HybridTranslationField,
        info_translations=ProductInfoTranslationField,
    )
    form_args = dict(
        photos=dict(
            description='上传GIF: 如果仅上传一张GIF图，系统将在创建post时自动'
                        '生成封面图。后续如果编辑post的图片，系统将不会再自动'
                        '生成封面图，必须手动上传。要手动指定封面图，应上传'
                        '两张图片, 第一张gif，第二张为封面图。',
        ),
        publish_at=dict(
            description='只有勾选is_active并且当前时间大于publish_at时，这个'
                        'post才会在客户端显示',
        ),
    )

    def format_photo(self, ctx, model, name):
        if model.photo_urls:
            return format_imgs(*model.photo_urls[:1])
        return ''

    def format_photo_urls(self, ctx, model, name):
        return format_imgs(*model.photo_urls)

    def format_related(self, ctx, model, name):
        return format_links(
            model_list_link(
                'Comment',
                flt_parent_id_equals=model.id,
            ),
            model_list_link(
                'Like',
                flt_parent_id_equals=model.id,
                flt_parent_type_equals='Post',
            ),
        )

    def format_vendor_links(self, ctx, model, name):
        return Markup(''.join('<p>{}</p>'.format(repr(vl))
                              for vl in model.vendor_links))

    def format_vendor_links_full(self, ctx, model, name):
        return Markup(''.join('<p>{} - {}</p>'.format(repr(vl), vl.url)
                              for vl in model.vendor_links))

    column_formatters = dict(
        photo=format_photo,
        photo_urls=format_photo_urls,
        vendor_links=format_vendor_links,
        vendor_links_full=format_vendor_links_full,
        related=format_related,
        message_translations=trans_hybrid_formatter,
        info_translations=trans_hybrid_product_info_formatter,
    )

    @property
    def can_delete(self):
        return self.has_roles('dev')

    def __init__(self, model, session, country=None, **kwargs):
        super().__init__(model, session, **kwargs)
        self.country = country

    def _post_filter(self, q):
        if self.country:
            q = q.filter(Post.country == self.country)
        return q

    def get_query(self):
        return self._post_filter(super().get_query().options(
            subqueryload('photos'),
        ))

    def get_count_query(self):
        return self._post_filter(super().get_count_query())

    def create_form(self, obj=None):
        """
        如果上传的图片只有一张，并且其格式为gif, 为它生成封面图

        生成封面图后，我们将其加入formdata, 这样后续代码都不用改动，包括获取
        图片尺寸、上传至s3等。
        """
        formdata = get_form_data()
        if (formdata and 'photos-0-url' in formdata and
                'photos-1-url' not in formdata):
            # a single gif is uploaded
            photo = formdata['photos-0-url']
            if photo.filename.endswith('.gif'):
                cover_fp = create_cover_for_gif(photo)
                name = photo.filename.split('.')[-2]
                formdata['photos-1-id'] = ''
                formdata['photos-1-url'] = FileStorage(
                    cover_fp, filename='{}-cover.jpeg'.format(name),
                    name='photos-1-url', content_type='image/jpeg',
                )
        return self._create_form_class(formdata, obj=obj)

    def on_model_change(self, form, model, is_created):
        if is_created:
            model.user = User.query.filter_by(
                name=current_app.config['PAGE_USER_NAME']).first()
        model.country = self.country
        # let's be explicit about this
        model.photos = PostPhoto.query.filter_by(post=model).all()
        model.media_type = Post.caculate_media_type(model)


_column_filters = [
    'is_active',
    # 'updated_at',
]
_column_list = [
    'id',
    'publish_at',
    'is_visible',
    'country',
    'message_translations',
    'info_translations',
    'comments_num',
    'likes_num',
    'related',
    'photo',
]
_column_details_list = [
    'id',
    'created_at',
    'publish_at',
    'is_active',
    'country',
    'message_translations',
    'info_translations',
    'comments_num',
    'likes_num',
    'related',
    'photo_urls',
]
_form_columns = [
    'is_active',
    'publish_at',
    'message_translations',
    'info_translations',
    'photos',
    'comments_num',
    'likes_num',
]


class AllPostAdmin(_BasePostAdmin):
    can_create = False
    column_filters = tuple(_column_filters + ['fb_id'])
    _extra_columns = [
        'media_type',
        'is_shopping',
        'sale_on',
        'price',
        'currency',
        'vendor_links',
        'fb_id',
    ]
    column_list = tuple(_column_list + _extra_columns)
    column_details_list = tuple(_column_details_list + _extra_columns)
    form_columns = tuple(_form_columns + _extra_columns)

    def is_visible(self):
        return self.has_roles('dev')


class PostAdmin(_BasePostAdmin):
    column_filters = tuple(_column_filters + ['fb_id'])
    column_labels = dict(
        is_from_fb='Is From Facebook Page?',
    )
    column_list = tuple(_column_list + [
        'is_from_fb',
        'fb_id',
    ])
    column_details_list = tuple(_column_details_list + [
        'is_from_fb',
        'fb_id',
    ])
    form_columns = tuple(_form_columns)

    def _post_filter(self, q):
        return super()._post_filter(q).filter(Post.is_shopping.is_(False))


class PreSaleProductAdmin(_BasePostAdmin):
    inline_models = (PostPhotoInlineForm(PostPhoto), VendorLink)
    column_default_sort = ('sale_on', True)
    column_filters = tuple(_column_filters)
    _extra_columns = [
        'sale_on',
        'price',
        'currency',
    ]
    column_list = tuple(_column_list + _extra_columns)
    column_details_list = tuple(_column_details_list + _extra_columns)
    form_columns = tuple(_form_columns + _extra_columns)
    form_args = dict(
        _BasePostAdmin.form_args,
        vendor_links=dict(
            description='若添加Vendor link, 商品将直接发售. 目前每个post只能'
                        '设置至多1个vendor link',
            # only allow a signle vendor link for each post
            max_entries=1,
        ),
        sale_on=dict(description='预计发售日期', validators=[DataRequired()]),
        price=dict(
            description='预计发售价格', validators=[DataRequired()]),
        currency=dict(
            description='预计发售货币', validators=[DataRequired()]),
    )

    def _post_filter(self, q):
        return super()._post_filter(q).filter(
            Post.is_shopping.is_(True),
            Post.sale_on.isnot(None),
        )

    def on_model_change(self, form, model, is_created):
        super().on_model_change(form, model, is_created)
        if model.vendor_links:
            model.sale_on = None
            vendor_link = model.vendor_links[0]
            model.price = vendor_link.price
            model.currency = vendor_link.currency
            model.updated_at = arrow.utcnow()
            flash('成功将商品{}设为在售商品'.format(model.id), 'success')


class OnSaleProductAdmin(_BasePostAdmin):
    inline_models = (PostPhotoInlineForm(PostPhoto), VendorLink)
    column_filters = tuple(_column_filters)
    column_list = tuple(_column_list + [
        'vendor_links',
    ])
    column_details_list = tuple(_column_details_list + [
        'vendor_links_full',
    ])
    form_columns = tuple(_form_columns + [
        'vendor_links',
    ])
    form_args = dict(
        _BasePostAdmin.form_args,
        # only allow a signle vendor link for each post
        vendor_links=dict(min_entries=1, max_entries=1),
    )

    def _post_filter(self, q):
        return super()._post_filter(q).filter(
            # return q.filter(
            Post.is_shopping.is_(True),
            Post.sale_on.is_(None),
        )

    def get_query(self):
        return super().get_query().options(
            subqueryload('vendor_links').subqueryload(VendorLink.vendor),
        )

    def on_model_change(self, form, model, is_created):
        super().on_model_change(form, model, is_created)
        if not is_created and not VendorLink.query.filter_by(
                post=model).first():
            # automatically set sale_on to a week from now
            model.sale_on = arrow.utcnow().shift(weeks=1).date()
            flash(
                '你删除了商品{id}的所有vendor link, 商品{id}被设为预售'
                '商品, 预售日期{date}'.format(
                    id=model.id, date=model.sale_on
                ), 'warning')
