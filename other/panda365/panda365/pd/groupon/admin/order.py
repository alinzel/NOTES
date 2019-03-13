from flask_admin.contrib.sqla.filters import (
    IntEqualFilter, BooleanEqualFilter)
from flask_admin.actions import action
from flask import flash
import sqlalchemy
from pd.admin.base import ModelView
from pd.admin.filters import IntEnumFilter
from pd.groupon.models.order import Order, OrderStatus
from pd.admin.format import format_links, model_list_link
from pd.facebook.models import User


class OrderAdmin(ModelView):
    can_export = True
    column_default_sort = ('created_at', True)
    column_filters = (
        'id',
        'email',
        IntEqualFilter(User.id, 'user_id'),
        BooleanEqualFilter(User.is_bot, 'is_bot'),
        IntEqualFilter(Order.batch_id, 'batch_id'),
        IntEqualFilter(Order.game_id, 'game_id'),
        IntEnumFilter(Order.status, 'status', OrderStatus),
    )
    column_list = (
        'id',
        'user',
        'country',
        'created_at',
        'updated_at',
        'status',
        'price',
        'shipping_price',
        'full_name',
        'complete_address',
        'postcode',
        'city',
        'province',
        'email',
        'phone',
        'links',
        'spec',
        'quantity',
    )

    column_sortable_list = (
        'created_at',
        'status',
        'updated_at'
    )

    column_export_list = [
        'id',
        'country',
        'created_at',
        'updated_at',
        'status',
        'price',
        'shipping_price',
        'full_name',
        'complete_address',
        'postcode',
        'city',
        'province',
        'email',
        'phone',
        'spec',
        'quantity',
        'product_id',
    ]

    def format_links(self, ctx, model, name):
        return format_links(
            model_list_link(
                'Product', text='product {}'.format(model.batch.product_id),
                flt_id_equals=model.batch.product_id,
            ),
            model_list_link(
                'Game', text='game {}'.format(model.game_id),
                flt_id_equals=model.game_id,
            ),
            model_list_link(
                'Payment', text='payment {}'.format(model.payment),
                flt_orderid_equals=model.id,
            ),
        )

    def format_country(self, ctx, model, name):
        return model.batch.country

    column_formatters = dict(
        country=format_country,
        links=format_links,
    )

    def export_format_product_id(self, ctx, model, name):
        return model.batch.product_id

    column_formatters_export = dict(
        country=format_country,
        product_id=export_format_product_id,
    )

    @property
    def can_edit(self):
        return self.has_roles('dev')

    def _set_status(self, ids, to_status, from_status):
        updated_orders = []
        for order in self.session.query(self.model).filter(
            self.model.id.in_(ids)
        ):
            is_set = order.set_status(to_status, from_status)
            if is_set:
                updated_orders.append(order)
        if updated_orders:
            flash('successfully set status of order {} from {} t'
                  'o {}'.format([d.id for d in updated_orders],
                                [o.name for o in from_status],
                                to_status.name
                                ), category='success')
            self.session.commit()
        else:
            flash('no order can be set to {}'.format(to_status.name))
        return updated_orders

    @action('shipped', 'Shipped',
            'Are you sure you want to set the status of this order as '
            '"Shipped"?')
    def action_shipped(self, ids):
        self._set_status(
            ids, OrderStatus.shipped, [OrderStatus.processing])

    def get_query(self):
        return super().get_query().join(User).filter(
            User.is_bot == sqlalchemy.sql.false())

    def get_count_query(self):
        return super().get_count_query().join(User).filter(
            User.is_bot == sqlalchemy.sql.false())
