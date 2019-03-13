import arrow
import factory
from sqlalchemy_utils import Currency
from pd.factory import (
    BaseFactory as _BaseFactory, InternationalizedFaker,
    InternationalizedProductInfo,
)
from pd.vendor.factory import VendorLinkFactory
from .models import Comment, Like, Post, PostPhoto, User, Country


class BaseFactory(_BaseFactory):

    class Meta:
        abstract = True

    fb_id = factory.Faker('uuid4')


class UserFactory(BaseFactory):

    class Meta:
        model = User

    name = factory.Faker('name')
    icon = factory.Faker('image_url')
    is_bot = False


class PostPhotoFactory(_BaseFactory):

    class Meta:
        model = PostPhoto

    url = factory.Faker('image_url')


class PostFactory(BaseFactory):

    class Meta:
        model = Post

    fb_page_id = factory.Faker('uuid4')
    message_translations = InternationalizedFaker('text')
    info_translations = InternationalizedProductInfo()
    user = factory.SubFactory(UserFactory)
    # by default we build a visible post
    is_active = True
    publish_at = factory.LazyFunction(lambda: arrow.utcnow().replace(hours=-1))


class PresalePostFactory(PostFactory):
    sale_on = factory.Faker('future_date')
    country = factory.Iterator(Country)
    price = 10
    currency = Currency('USD')


class OnsalePostFactory(PostFactory):
    vendor_links = factory.RelatedFactory(VendorLinkFactory, 'post')
    country = factory.Iterator(Country)


class CommentFactory(BaseFactory):

    class Meta:
        model = Comment

    message = factory.Faker('sentence')
    photo_url = factory.Faker('image_url')
    user = factory.SubFactory(UserFactory)
    parent = factory.SubFactory(PostFactory)


class ReplyFactory(CommentFactory):
    parent = factory.SubFactory(CommentFactory)


class LikeFactory(BaseFactory):

    class Meta:
        model = Like

    parent = factory.SubFactory(PostFactory)
    user = factory.SubFactory(UserFactory)
