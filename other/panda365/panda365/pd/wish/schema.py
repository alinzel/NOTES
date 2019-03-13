from marshmallow.fields import Boolean, DateTime, String, List, Nested
from pd.api.fields import Enum, ProductInfo
from pd.api.schema import ModelSchema
from pd.constants import Country
from .models import Wish, WishPrice, WishStatus, Vote


class VoteSchema(ModelSchema):

    class Meta:
        model = Vote
        fields = (
            'id',
            'updated_at',
            'next_vote_at',
            'count',
            'can_vote',
        )
    next_vote_at = DateTime(description='下次可投票的时间')
    can_vote = Boolean(description='当前是否可以投票')


class WishPriceSchema(ModelSchema):
    class Meta:
        model = WishPrice
        fields = (
            'country',
            'price',
            'currency',
        )
    country = Enum(Country)


class WishSchema(ModelSchema):

    class Meta:
        model = Wish
        fields = (
            'id',
            'can_vote',
            'created_at',
            'message',
            'tip',
            'media_urls',
            'votes_num',
            'votes_target',
            'comments_num',
            'status',
            'info',
            # user vote status
            'my_vote',
            # price specific to the currency country in request
            'country_price',
        )

    can_vote = Boolean(description='wish是否接受投票')
    status = Enum(WishStatus)
    tip = String()
    message = String()
    media_urls = List(String(), description='媒体文件链接')
    my_vote = Nested(
        VoteSchema, description='若请求包含auto_token, 则包含用户投票情况')
    country_price = Nested(WishPriceSchema)
    info = ProductInfo()
