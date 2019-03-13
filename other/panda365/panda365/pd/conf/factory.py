import factory
from pd.factory import BaseFactory
from .models import Conf


class ConfFactory(BaseFactory):

    class Meta:
        model = Conf

    name = factory.Faker('word')
    min_version = 2
    latest_version = 4
    description = factory.Faker('text')
