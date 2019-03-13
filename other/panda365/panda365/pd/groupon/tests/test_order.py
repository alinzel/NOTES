from blinker import signal
from pd.facebook.factory import UserFactory
from pd.groupon.factory import BatchFactory, OrderFactory
from pd.groupon.models.order import OrderStatus
from pd.payment.factory import PaymentFactory
import arrow
import pytest


def test_admin_games(db_session):
    """
    scenario:

    一个期次中，有3个用户创建了订单，把期次结束，三个用户的订单的状态会改变，但是订单的update_at不会改变


    """
    users = UserFactory.create_batch(3)
    batch = BatchFactory(total_shares=2)
    assert batch.sold_num == 0
    game = batch.create_game()
    db_session.commit()
    assert game.left_shares == 2

    o1 = OrderFactory(game=game, user=users[0])
    # time.sleep(2)
    assert o1.status == OrderStatus.payment_pending
    assert batch.sold_num == 0
    payment = PaymentFactory(object=o1, user=o1.user)
    signal('payment_created').send(payment)
    assert o1.status == OrderStatus.payment_processing
    signal('payment_succeeded').send(payment)
    assert batch.sold_num == 1
    # game shares should decrease by 1
    assert o1.status == OrderStatus.paid
    # should link order to its successful payment
    # time.sleep(2)
    assert o1.payment == payment
    assert game.left_shares == 1
    db_session.commit()

    o2 = OrderFactory(game=game, user=users[1])
    assert o2.status == OrderStatus.payment_pending
    game.left_shares = 0
    db_session.commit()
    assert game.left_shares == 0
    assert not game.is_running
    signal('game_finished').send(game)
    assert o1.status == OrderStatus.processing
    # assert o1.updated_at == arrow.utcnow()


def test_order_status(db_session):
    """
    scenario:

    一个期次中，有3个用户创建了订单，其中user0和user2进行了支付。
    当user2完成支付时，期次中的订单状态应该对应的进行变化
    """
    users = UserFactory.create_batch(3)
    batch = BatchFactory(total_shares=2)
    assert batch.sold_num == 0
    game = batch.create_game()
    db_session.commit()
    assert game.left_shares == 2

    o1 = OrderFactory(game=game, user=users[0])
    assert o1.status == OrderStatus.payment_pending
    assert batch.sold_num == 0
    payment = PaymentFactory(object=o1, user=o1.user)
    signal('payment_created').send(payment)
    assert o1.status == OrderStatus.payment_processing
    signal('payment_succeeded').send(payment)
    assert batch.sold_num == 1
    # game shares should decrease by 1
    assert o1.status == OrderStatus.paid
    # should link order to its successful payment
    assert o1.payment == payment
    assert game.left_shares == 1
    db_session.commit()

    o2 = OrderFactory(game=game, user=users[1])
    assert o2.status == OrderStatus.payment_pending
    o3 = OrderFactory(game=game, user=users[2])
    assert o3.status == OrderStatus.payment_pending
    db_session.commit()
    # o3成功后，期次团购成功
    payment = PaymentFactory(object=o3, user=o3.user)
    signal('payment_created').send(payment)
    signal('payment_succeeded').send(payment)
    assert batch.sold_num == 2
    assert o3.status == OrderStatus.processing == o1.status
    # 未支付的订单在批次结束前保持未支付状态
    assert o2.status == OrderStatus.payment_pending
    assert not game.is_running


@pytest.mark.parametrize('payment_result,expected_status', [
    ['payment_failed', OrderStatus.payment_failed],
    ['payment_canceled', OrderStatus.canceled],
])
def test_payment_status(db_session, user, payment_result, expected_status):
    batch = BatchFactory()
    game = batch.create_game()
    db_session.commit()

    o1 = OrderFactory(game=game, user=user)
    payment = PaymentFactory(object=o1, user=user)
    signal('payment_created').send(payment)
    assert o1.status == OrderStatus.payment_processing
    signal(payment_result).send(payment)
    assert o1.status == expected_status


def test_batch_finish(db_session):
    """
    在批次结束前有两个订单，一个是未支付，一个是支付处理中
    """
    batch = BatchFactory(total_shares=3)
    users = UserFactory.create_batch(2)
    game = batch.create_game()
    db_session.commit()

    o1 = OrderFactory(game=game, user=users[0])
    o2 = OrderFactory(game=game, user=users[1])
    payment = PaymentFactory(object=o1, user=o1.user)
    signal('payment_created').send(payment)
    # 批次结束
    batch.end_at = arrow.utcnow().shift(minutes=-1)
    batch.finish()
    db_session.commit()
    # 未支付订单应被取消
    assert o2.status == OrderStatus.canceled
    # 支付处理中的订单不变
    assert o1.status == OrderStatus.payment_processing

    signal('payment_succeeded').send(payment)
    # order should be associated with a virtual game
    assert o1.game_id != game.id
    # no new game should be created
    assert not batch.get_latest_game()
    assert o1.status == OrderStatus.processing


@pytest.mark.db
def test_set_status():
    batch = OrderFactory.build(status=OrderStatus.payment_pending)
    batch.set_status(OrderStatus.paid, [OrderStatus.payment_processing])
    assert batch.status == OrderStatus.payment_pending
    batch.set_status(
        OrderStatus.payment_processing, [OrderStatus.payment_pending])
    assert batch.status == OrderStatus.payment_processing
