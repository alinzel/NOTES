from pd.groupon.factory import BatchFactory, OrderFactory
from pd.payment.factory import PaymentFactory
import pytest


@pytest.fixture
def batch(db_session):
    return BatchFactory()


@pytest.fixture
def game(batch, db_session):
    game = batch.create_game()
    db_session.commit()
    return game


@pytest.fixture
def order(game, user):
    return OrderFactory(user=user, game=game)


@pytest.fixture
def payment(order, user):
    return PaymentFactory(
        user=user,
        object=order,
        amount=order.price,
        currency=order.currency,
    )
