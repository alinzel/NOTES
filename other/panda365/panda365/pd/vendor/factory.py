import factory
from sqlalchemy_utils import Currency
from pd.factory import BaseFactory
from .models import Vendor, VendorLink


class VendorFactory(BaseFactory):

    class Meta:
        model = Vendor

    name = factory.Faker('word')
    logo_url = factory.Faker('image_url')


class VendorLinkFactory(BaseFactory):

    class Meta:
        model = VendorLink

    price = 10
    currency = Currency('USD')
    url = factory.Faker('uri')
    vendor = factory.SubFactory(VendorFactory)
