from .models import Payment, PaymentStatus, Vendors
from marshmallow import validates, ValidationError
from marshmallow.fields import String
from pd.api.fields import ModelPKField, Enum
from pd.api.schema import Schema, ModelSchema
from pd.auth.jwt import current_user_data
from pd.groupon.models import Order, OrderStatus


class CheckoutSchema(Schema):
    order = ModelPKField(
        Order,
        # only allow my own orders
        lambda: Order.user_id == current_user_data['id'],
        required=True, description='订单号', load_from='order_id',
    )
    return_url = String(required=True, description='客户端回掉URL')

    @validates('order')
    def validate_order(self, value):
        if value.status != OrderStatus.payment_pending:
            raise ValidationError(
                'status of order is not payment_pending')


payment_fields = (
    'id',
    'method',
    'amount',
    'currency',
    'status',
    'vendor',
    'transaction_id',
    'ref_id',
    'payment_url',
)


class PaymentSchema(ModelSchema):

    class Meta:
        model = Payment
        fields = payment_fields

    status = Enum(PaymentStatus)
    vendor = Enum(Vendors)
