import factory
from sqlalchemy_utils import Currency
from pd.constants import Country
from pd.factory import (
    BaseFactory, InternationalizedFaker, InternationalizedProductInfo,
)
from pd.facebook.factory import UserFactory
from .models import Wish, WishPrice, Vote, WishMedia, Tip


class TipFactory(BaseFactory):

    class Meta:
        model = Tip

    message_translations = InternationalizedFaker('text')


class WishMediaFactory(BaseFactory):

    class Meta:
        model = WishMedia

    url = factory.Faker('image_url')


class WishPriceFactory(BaseFactory):

    class Meta:
        model = WishPrice

    country = factory.Iterator(Country)
    price = 10
    currency = Currency('USD')


class WishFactory(BaseFactory):

    class Meta:
        model = Wish

    media = factory.RelatedFactory(WishMediaFactory, 'wish')
    message_translations = InternationalizedFaker('text')
    info_translations = InternationalizedProductInfo()
    prices = factory.RelatedFactory(WishPriceFactory, 'wish')
    tip = factory.SubFactory(TipFactory)
    votes_target = 3


class VoteFactory(BaseFactory):

    class Meta:
        model = Vote

    user = factory.SubFactory(UserFactory)
