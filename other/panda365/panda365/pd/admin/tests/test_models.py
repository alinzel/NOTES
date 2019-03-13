from ..factory import AdminUserFactory, AdminRoleFactory


def test_models(db_session):
    dev_role = AdminRoleFactory.create()
    assert str(dev_role)
    user = AdminUserFactory.create(roles=[dev_role])
    assert str(user)
    assert user.roles == [dev_role]


def test_models2(db_session):
    dev_role = AdminRoleFactory.create(name='dev')
    assert str(dev_role)
    user = AdminUserFactory.create(roles=[dev_role])
    assert str(user)
    assert user.roles == [dev_role]
