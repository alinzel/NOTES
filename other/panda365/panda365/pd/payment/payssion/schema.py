from marshmallow import ValidationError, validates_schema
from marshmallow.fields import String, Float
from marshmallow.validate import Length
from pd.api.schema import Schema
from pd.api.fields import Enum
from pd.ext import payssion
from pd.payment import schema
from pd.payment.models import Payment
from .client import PaymentStatus as PayssionPaymentStatus


class PaymentSchema(schema.PaymentSchema):

    class Meta:
        model = Payment
        fields = list(schema.payment_fields) + ['payment_url']

    payment_url = String(description='客户端支付URL')


class CheckoutSchema(schema.CheckoutSchema):
    method = String(
        validate=Length(min=1), description='payssion支付方式名称(pm_id)',
    )


class CallbackSchema(Schema):
    transaction_id = String(required=True)
    order_id = String(required=True)


class TransactionSchema(Schema):
    transaction_id = String(required=True)
    state = Enum(PayssionPaymentStatus, required=True)
    amount = Float(required=True)
    currency = String(required=True)
    order_id = String(required=True)
    pm_id = String(required=True)


class NotifySchema(TransactionSchema):

    signature = String(required=True, load_from='notify_sig')

    @validates_schema(pass_original=True)
    def validate_signature(self, data, original):
        # note we need to use the original data to verify the signature
        # data is converted already
        try:
            if not payssion.client.verify_notify_signature(
                original['pm_id'],
                original['amount'],
                original['currency'],
                original['order_id'],
                original['state'],
                original['notify_sig'],
            ):
                raise ValidationError('signature verification failed')
        except KeyError:
            raise ValidationError('signature verification failed')
