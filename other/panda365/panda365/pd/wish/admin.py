from flask import Markup, flash, url_for
from flask_admin import helpers as h
from flask_admin.model.form import InlineFormAdmin
from pd.admin.base import ModelView
from pd.admin.fields import (
    S3ImageUploadField, HybridTranslationField, ProductInfoTranslationField,
)
from pd.admin.format import (
    trans_hybrid_formatter, format_progress, format_imgs, format_links,
    model_list_link, trans_hybrid_product_info_formatter,
)
from .models import Tip, WishMedia, WishPrice


class WishMediaInlineForm(InlineFormAdmin):
    form_columns = ('id', 'url')
    form_label = 'Photos'
    form_overrides = dict(
        url=S3ImageUploadField,
    )
    form_args = dict(
        url=dict(s3_directory='images/wishes'),
    )


class WishAdmin(ModelView):
    can_create = True
    can_delete = True
    inline_models = (
        WishMediaInlineForm(WishMedia),
        WishPrice,
    )
    column_default_sort = ('vote_progress', True)
    column_list = (
        'id',
        'created_at',
        'tip',
        'status',
        'comments_num',
        'prices',
        'message_translations',
        'info_translations',
        'vote_progress',
        'media',
        'links',
    )
    column_details_list = (
        'id',
        'created_at',
        'tip',
        'status',
        'comments_num',
        'prices',
        'message_translations',
        'info_translations',
        'vote_progress',
        'media_urls',
        'links',
    )
    column_sortable_list = (
        'created_at',
        'status',
        'vote_progress',
    )
    form_overrides = dict(
        message_translations=HybridTranslationField,
        info_translations=ProductInfoTranslationField,
    )
    form_columns = (
        'tip',
        'message_translations',
        'info_translations',
        'votes_target',
        'admin_votes_num',
        'status',
    )
    form_args = dict(
        tip=dict(default=Tip.random),
        prices=dict(min_entries=1),
        admin_votes_num=dict(
            label='预设投票数',
            description='客户端显示投票数 = 预设投票数 + 真实用户投票数',
        ),
    )
    column_labels = dict(
        votes_target='需要的总投票数',
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
        return ''  # pragma: no cover

    def format_vote_progress(self, ctx, model, name):
        return format_progress(
            model.votes_num, model.votes_target,
            text='''
            <p>
            (<span title="预设投票数">{}</span> +
            <strong title="真实投票数">{}</strong>) /
            <strong title="目标投票数">{}</strong>
            </p>
            '''.format(
                model.admin_votes_num,
                model.real_votes_num,
                model.votes_target,
            )
        )

    def format_links(self, ctx, model, name):
        return format_links(
            model_list_link(
                'Vote',
                flt_wish_id_equals=model.id,
            ),
            model_list_link(
                'Comment',
                endpoint='wish_comment',
                flt_parent_id_equals=model.id,
            )
        )

    def format_prices(self, ctx, model, name):
        tpl = '''
        <div>
            <span class="label label-default">{}</span>
            <p>{} {}</p>
        </div>'''
        parts = [tpl.format(
            p.country.admin_label, p.price, p.currency
        ) for p in model.prices]
        return Markup(''.join(parts))

    column_formatters = dict(
        message_translations=trans_hybrid_formatter,
        info_translations=trans_hybrid_product_info_formatter,
        vote_progress=format_vote_progress,
        media=format_media,
        media_urls=format_media_urls,
        links=format_links,
        prices=format_prices,
    )

    def create_form(self, obj=None):
        form = super().create_form(obj)
        if not h.is_form_submitted() and not form.tip.data:
            flash(Markup(
                '数据库里没有任何Tip. 请在创建Wish前先'
                '<a href="{}">创建Tip</a>'.format(
                    url_for('tip.create_view'),
                )),
                'warning'
            )
        form.tip.description = '由系统在数据库中随机选取'
        return form


class TipAdmin(ModelView):
    can_create = True
    column_default_sort = ('id', True)
    column_list = (
        'id',
        'message_translations',
    )
    form_overrides = dict(
        message_translations=HybridTranslationField,
    )
    column_formatters = dict(
        message_translations=trans_hybrid_formatter,
    )

    @property
    def can_delete(self):
        return self.has_roles('dev')


class VoteAdmin(ModelView):
    column_list = (
        'id',
        'updated_at',
        'user',
        'wish',
        'count',
    )
    form_columns = (
        'user',
        'wish',
        'count',
        'updated_at',
    )
    column_filters = (
        'wish_id',
        'user_id',
    )

    def format_wish(self, ctx, model, name):
        return model_list_link(
            'Wish',
            flt_id_equals=model.wish_id,
            text='wish[{}]'.format(model.wish_id))

    column_formatters = dict(
        wish=format_wish,
    )

    @property
    def can_create(self):
        return self.has_roles('dev')

    @property
    def can_edit(self):
        return self.has_roles('dev')
