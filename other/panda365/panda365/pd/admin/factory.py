from datetime import datetime
import factory
from pd.factory import BaseFactory
from .models import AdminUser, AdminRole


class AdminUserFactory(BaseFactory):

    class Meta:
        model = AdminUser

    email = factory.Faker('email')
    password = 'admin4u'
    active = True
    confirmed_at = datetime(2017, 1, 1)


class AdminRoleFactory(BaseFactory):

    class Meta:
        model = AdminRole

    name = factory.Sequence(lambda n: 'role-{}'.format(n))
