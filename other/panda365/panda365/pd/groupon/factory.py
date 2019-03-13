import arrow
import factory
from pd.constants import Country
from pd.facebook.factory import UserFactory
from pd.factory import (
    BaseFactory, InternationalizedFaker, InternationalizedProductInfo,
    PositiveDecimal,
)
from .models import (
    Batch, BatchSpec, ProductMedia, Product, Spec, SpecOption, Order,
    OrderStatus, Category,
)
from sqlalchemy_utils import Currency


class ProductMediaFactory(BaseFactory):

    class Meta:
        model = ProductMedia

    url = factory.Faker('image_url')


class SpecOptionFactory(BaseFactory):

    class Meta:
        model = SpecOption

    value_translations = InternationalizedFaker('word')


class SpecFactory(BaseFactory):

    class Meta:
        model = Spec

    name_translations = InternationalizedFaker('word')


class CategoryFactory(BaseFactory):

    class Meta:
        model = Category

    name_translations = InternationalizedFaker('word')


class ProductFactory(BaseFactory):

    class Meta:
        model = Product

    media = factory.RelatedFactory(ProductMediaFactory, 'product')
    title_translations = InternationalizedFaker('text')
    description_translations = InternationalizedFaker('text')
    info_translations = InternationalizedProductInfo()


class BatchSpecFactory(BaseFactory):

    class Meta:
        model = BatchSpec

    spec = factory.SubFactory(SpecFactory)

    @factory.post_generation
    def options(self, create, extracted, **kwargs):
        if extracted:
            for option in extracted:
                self.options.append(option)


class BatchFactory(BaseFactory):

    class Meta:
        model = Batch

    country = Country.MY
    product = factory.SubFactory(ProductFactory)
    category = factory.SubFactory(CategoryFactory)
    price = PositiveDecimal()
    currency = Currency('USD')
    market_price = PositiveDecimal()
    market_currency = Currency('USD')
    shipping_price = PositiveDecimal()
    direct_buy_url = factory.Faker('url')

    total_shares = 5
    start_at = factory.LazyFunction(arrow.utcnow)
    end_at = factory.LazyFunction(lambda: arrow.utcnow().shift(days=5))
    sort_weight = 0


class AddressDictFactory(factory.DictFactory):
    """
    这个factory的返回值是一个dict，因为它的model AddressMixin并不是一个真正
    的model，而是一个mixin
    """
    full_name = factory.Faker('name')
    complete_address = factory.Faker('address')
    postcode = factory.Faker('postcode')
    city = factory.Faker('city')
    province = factory.Faker('state')
    phone = factory.Faker('phone_number')


class OrderFactory(BaseFactory):

    class Meta:
        model = Order

    email = factory.Faker('email')
    status = OrderStatus.payment_pending
    user = factory.SubFactory(UserFactory)
    spec = factory.Faker('word')
    quantity = 1

    @classmethod
    def _build_address(cls, model_cls, **kwargs):
        addr = AddressDictFactory()
        for k, v in addr.items():
            kwargs.setdefault(k, v)
        return kwargs

    @classmethod
    def _create(cls, model_cls, *args, **kwargs):
        kwargs = cls._build_address(model_cls, **kwargs)
        return super()._create(model_cls, *args, **kwargs)

    @classmethod
    def _build(cls, model_cls, *args, **kwargs):
        kwargs = cls._build_address(model_cls, **kwargs)
        return super()._build(model_cls, *args, **kwargs)
