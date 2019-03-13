from .models import (
    Game, Product, Order, OrderStatus, Category, BatchSpec, SpecOption, Spec)
from marshmallow.fields import (
    Nested, String, DateTime, Email, Integer, List)
from pd.api.fields import ProductInfo, Enum
from pd.api.schema import ModelSchema, Schema
from pd.constants import Country
from pd.payment.schema import PaymentSchema
from pd.facebook.schema import UserSchema


class ProductSchema(ModelSchema):

    class Meta:
        model = Product
        fields = (
            'id',
            'title',
            'description',
            'info',
            'media_urls',
        )
    title = String()
    description = String()
    info = ProductInfo()
    media_urls = List(String(), description='媒体文件链接')


class SpecSchema(ModelSchema):
    class Meta:
        model = Spec
        fields = (
            'name',
        )
    name = String()


class SpecOptionSchema(ModelSchema):
    class Meta:
        model = SpecOption
        fields = (
            'value',
        )
    value = String()


class BatchSpecSchema(ModelSchema):
    class Meta:
        model = BatchSpec
        fields = (
            'spec',
            'options',
        )
    spec = String()
    options = List(String())


class GameSchema(ModelSchema):

    class Meta:
        model = Game
        fields = (
            'id',
            'country',
            'batch_id',
            'price',
            'currency',
            'market_price',
            'market_currency',
            'shipping_price',
            'total_shares',
            'created_at',
            'start_at',
            'end_at',
            'product',
            'left_shares',
            'sold_shares',
            'direct_buy_url',
            'sold_num',
            'issue_id',
            'order',
            'sort_weight',
            'category_id',
            'users',
            'specs',
        )

    created_at = DateTime(description='期次开始时间')
    country = Enum(Country)
    product = Nested(ProductSchema)
    specs = List(Nested(BatchSpecSchema))
    sold_num = Integer()
    order = Nested('OrderSchema', exclude=('game',))
    users = List(Nested(UserSchema, only='icon_url'))
    sold_shares = Integer(description='期次已售份数')


class OrderCreateSchema(Schema):
    email = Email(required=True)
    game_id = Integer(required=True)
    # address
    full_name = String(required=True)
    complete_address = String(required=True)
    postcode = String(required=True)
    city = String(required=True)
    province = String(required=True)
    phone = String(required=True)
    quantity = Integer(allow_none=True, missing=1)
    spec = String(allow_none=True, missing='')


class OrderSchema(ModelSchema):

    class Meta:
        model = Order
        fields = [
            'id',
            'created_at',
            'email',
            'game_id',
            'game',
            'status',
            'full_name',
            'complete_address',
            'postcode',
            'city',
            'province',
            'phone',
            'spec',
            'quantity',
            'payment',
        ]

    status = Enum(OrderStatus)
    game = Nested(GameSchema, exclude=('sold_num',))
    payment = Nested(PaymentSchema, exclude=('transaction_id',))


class CategorySchema(ModelSchema):

    class Meta:
        model = Category
        fields = (
            'id',
            'name',
            'sort_weight',
        )
    name = String()
