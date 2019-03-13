from functools import lru_cache, partial
import factory
from factory.declarations import OrderedDeclaration
from faker import Faker
from flask import current_app

from pd.sqla import lazy_session


class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):

    class Meta:
        abstract = True
        sqlalchemy_session = lazy_session
        sqlalchemy_session_persistence = 'commit'


class InternationalizedFaker(OrderedDeclaration):

    def __init__(self, fake, *args):
        """
        returns a dict like `{'en': Faker(locale='en').text()}` according to
        the config BABEL_SUPPORTED_LOCALES.

        :param str fake: name of the fake to use, e.g., "text", "word"
        :param args: additional args passed to the fake
        """
        self.fake = fake
        self.args = args

    @lru_cache()
    def _get_factory(self, locale):
        return Faker(locale=locale)

    def format(self, fake_func):
        """
        given the fake function from a locale, return formatted content.

        By default, the return value of the fake function is returned.
        """
        return fake_func(*self.args)

    def evaluate(self, *args, **kwargs):
        ret = {}
        for locale in current_app.config['BABEL_SUPPORTED_LOCALES']:
            fake_func = getattr(self._get_factory(locale), self.fake)
            ret[locale] = self.format(fake_func)
        return ret


class InternationalizedProductInfo(InternationalizedFaker):
    """
    returns a translation object formatted to be used as product info.
    """

    def __init__(self):
        super().__init__('word')

    def format(self, fake_func):
        return '{}:{}'.format(fake_func(), fake_func())


PositiveDecimal = partial(
    factory.Faker, 'pydecimal',
    left_digits=2, right_digits=2, positive=True,
)
