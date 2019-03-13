from flask_admin.contrib.sqla.filters import (
    IntEqualFilter, DateTimeBetweenFilter)
from pd.admin.base import ModelView
from pd.admin.filters import IntEnumFilter
from pd.facebook.models import User
from pd.payment.models import (
    Payment, PaymentStatus, Vendors)
from pd.admin.format import format_links, model_list_link


class PaymentDevAdmin(ModelView):
    can_edit = True

    def is_visible(self):
        return self.has_roles('dev')

    column_filters = (
        IntEqualFilter(User.id, 'user_id'),
        'method',
        IntEnumFilter(Payment.status, 'status', PaymentStatus),
        IntEnumFilter(Payment.vendor, 'vendor', Vendors),
        DateTimeBetweenFilter(Payment.created_at, 'created_at(UTC)'),
        DateTimeBetweenFilter(Payment.updated_at, 'updated_at(UTC)'),
        'id',
        'transaction_id',
        'ref_id',
    )


class PaymentAdmin(ModelView):
    can_export = True
    column_list = [
        'id',
        'user',
        'created_at',
        'updated_at',
        'vendor',
        'amount',
        'currency',
        'method',
        'status',
        'order',
        'extra_data',
    ]

    column_filters = (
        IntEqualFilter(User.id, 'user_id'),
        IntEqualFilter(Payment.object_id, 'order_id'),
        'method',
        IntEnumFilter(Payment.status, 'status', PaymentStatus),
        IntEnumFilter(Payment.vendor, 'vendor', Vendors),
        DateTimeBetweenFilter(Payment.created_at, 'created_at(UTC)'),
        DateTimeBetweenFilter(Payment.updated_at, 'updated_at(UTC)'),
        'id',
    )

    column_sortable_list = (
        'created_at',
        'updated_at',
        'status',
        'amount',
    )

    def format_order(self, ctx, model, name):
        return format_links(
            model_list_link(
                'Order', text='order {}'.format(model.object_id),
                flt_id_equals=model.object_id,
            ),
        )

    column_formatters = dict(
        order=format_order,
    )
