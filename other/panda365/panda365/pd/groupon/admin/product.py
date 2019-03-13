from flask_admin.model.form import InlineFormAdmin
from pd.admin.base import ModelView
from pd.admin.fields import (
    S3ImageUploadField, HybridTranslationField, ProductInfoTranslationField,
)
from pd.admin.format import (
    trans_hybrid_formatter, format_imgs, format_links,
    model_list_link, trans_hybrid_product_info_formatter,
)
from pd.groupon.models import ProductMedia


class ProductMediaInlineForm(InlineFormAdmin):
    form_columns = ('id', 'url')
    form_label = 'Photos'
    form_overrides = dict(
        url=S3ImageUploadField,
    )
    form_args = dict(
        url=dict(s3_directory='images/products'),
    )


class ProductAdmin(ModelView):
    can_create = True
    can_delete = True
    inline_models = (
        ProductMediaInlineForm(ProductMedia),
    )
    column_default_sort = ('created_at', True)
    column_list = (
        'id',
        'created_at',
        'comments_num',
        'title_translations',
        'info_translations',
        'description_translations',
        'media',
        'links',
    )
    column_details_list = (
        'id',
        'created_at',
        'comments_num',
        'title_translations',
        'info_translations',
        'media_urls',
        'links',
    )
    column_sortable_list = (
        'created_at',
    )
    form_overrides = dict(
        title_translations=HybridTranslationField,
        description_translations=HybridTranslationField,
        info_translations=ProductInfoTranslationField,
    )
    form_columns = (
        'title_translations',
        'description_translations',
        'info_translations',
    )
    column_filters = (
        'id',
    )

    def format_media(self, ctx, model, name):
        if model.media_urls:
            return format_imgs(*model.media_urls[:1])
        return ''

    def format_media_urls(self, ctx, model, name):
        if model.media_urls:
            return format_imgs(*model.media_urls)
        return ''

    def format_links(self, ctx, model, name):
        return format_links(
            model_list_link(
                'Comment',
                endpoint='product_comment',
                flt_parent_id_equals=model.id,
            )
        )

    column_formatters = dict(
        title_translations=trans_hybrid_formatter,
        description_translations=trans_hybrid_formatter,
        info_translations=trans_hybrid_product_info_formatter,
        media=format_media,
        media_urls=format_media_urls,
        links=format_links,
    )


class CategoryAdmin(ModelView):
    can_create = True
    can_edit = True

    column_list = (
        'id',
        'name_translations',
        'sort_weight',
    )

    column_default_sort = ('sort_weight', True)

    column_sortable_list = (
        'sort_weight',
        'id',
    )

    column_filters = (
        'id',
    )
    form_overrides = dict(
        name_translations=HybridTranslationField,
    )


class SpecAdmin(ModelView):
    can_create = True
    can_edit = True

    form_overrides = dict(
        name_translations=HybridTranslationField,
    )


class SpecOptionAdmin(ModelView):
    can_create = True
    can_edit = True

    form_overrides = dict(
        value_translations=HybridTranslationField,
    )
