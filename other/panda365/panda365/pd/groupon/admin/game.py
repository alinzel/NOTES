from wtforms.validators import ValidationError, NumberRange
from flask import request
from pd.admin.base import ModelView
from pd.admin.format import format_progress
from pd.groupon.models import Product, Batch
from pd.groupon.models.game import BatchFinishStatus
from pd.admin.filters import IntEnumFilter
from flask_admin.contrib.sqla.filters import IntEqualFilter


def validate_end_at(form, field):
    if form.start_at.data and field.data:
        if form.start_at.data >= field.data:
            raise ValidationError('结束时间必须大于开始时间')


class BatchSpecAdmin(ModelView):
    can_create = True
    can_edit = True
    can_delete = True


class BatchAdmin(ModelView):
    can_create = True
    can_edit = True
    column_default_sort = ('start_at', True)
    form_columns = (
        'product',
        'category',
        'country',
        'price',
        'currency',
        'market_price',
        'market_currency',
        'shipping_price',
        'total_shares',
        'start_at',
        'end_at',
        'direct_buy_url',
        'sold_num',
        'sort_weight',
    )

    column_sortable_list = (
        'start_at',
        'end_at',
        'sold_num',
        'finish_status',
        'sort_weight',
    )

    column_filters = (
        'id',
        IntEqualFilter(Product.id, 'product_id'),
        IntEnumFilter(Batch.finish_status, 'status', BatchFinishStatus),
    )

    form_args = dict(
        end_at=dict(
            validators=[validate_end_at]),
        total_shares=dict(validators=[NumberRange(min=1)]),
        sort_weight=dict(
            description='控制期次在首页的顺序。值越大排序越靠前。默认为0。',
            validators=[NumberRange(min=0)]
        ),
    )

    disabled_fields_on_edit_form = (
        'country',
        'price',
        'currency',
        'shipping_price',
    )

    @property
    def form_widget_args(self):
        if not request:
            return {}
        if 'edit_view' in request.endpoint:
            return {
                k: dict(disabled=True)
                for k in self.disabled_fields_on_edit_form
            }

    def on_model_change(self, form, model, is_created):
        if is_created:
            self.session.flush()
            model.create_game()


class GameAdmin(ModelView):
    can_create = False
    can_edit = True
    column_default_sort = ('created_at', True)

    form_columns = (
        'market_price',
        'market_currency',
        'shipping_price',
        'start_at',
        'end_at',
        'direct_buy_url',
        'total_shares',
        'left_shares',
        'sort_weight',
    )

    column_list = [
        'category',
        'batch_id',
        'issue_id',
        'product',
        'country',
        'price',
        'groupon_progress',
        'currency',
        'market_price',
        'market_currency',
        'shipping_price',
        'created_at',
        'start_at',
        'end_at',
        'direct_buy_url',
        'sold_num',
        'sort_weight',
    ]

    column_details_list = column_list

    column_sortable_list = (
        'start_at',
        'end_at',
        'sold_num',
        'issue_id',
        'groupon_progress',
        'sort_weight',
    )

    column_filters = (
        'id',
        IntEqualFilter(Product.id, 'product_id'),
        IntEqualFilter(Batch.id, 'batch_id'),
    )

    disabled_fields_on_edit_form = (
        'start_at',
        'end_at',
    )

    form_args = dict(
        sort_weight=dict(
            description='控制期次在首页的顺序。值越大排序越靠前。默认为0。',
            validators=[NumberRange(min=0)]
        ),
        left_shares=dict(
            description='修改后剩余份数必须小于修改前剩余份数',
        )
    )

    def format_groupon_progress(self, ctx, model, name):
        return format_progress(
            model.sold_shares, model.total_shares,
        )

    column_formatters = dict(
        groupon_progress=format_groupon_progress,
    )

    def on_model_change(self, form, model, is_created):
        model.batch.check_game_finish(model)
        model.check_left_shares()
