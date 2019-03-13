from blinker import signal
from pd.groupon.models import OrderStatus
from pd.groupon.models.game import BatchFinishStatus
from pd.groupon.factory import BatchFactory, OrderFactory
from pd.groupon.tasks import (
    check_for_imminent_batches, finish_batch, close_payment_processing_orders,
)
from unittest.mock import patch, Mock
import arrow
import pytest


@pytest.mark.db
def test_imminent_batches():
    b1 = BatchFactory(
        start_at=arrow.get('2017-01-01'),
        end_at=arrow.get('2017-01-02 00:01:00'),
    )
    BatchFactory(
        start_at=arrow.get('2017-01-01'),
        end_at=arrow.get('2017-01-02 01:15:00'),
    )
    with patch('pd.groupon.tasks.arrow') as mock_arrow:
        with patch('pd.groupon.tasks.finish_batch') as mock_finish_batch:
            # no imminent batches
            mock_arrow.utcnow.return_value = arrow.get('2017-01-01')
            check_for_imminent_batches()
            assert not mock_finish_batch.apply_async.called

            # b1 imminent
            mock_arrow.utcnow.return_value = arrow.get('2017-01-02')
            check_for_imminent_batches()
            assert mock_finish_batch.apply_async.call_count == 1
            _, kwargs = mock_finish_batch.apply_async.call_args
            assert kwargs == dict(
                kwargs=dict(batch_id=b1.id),
                eta=b1.end_at
            )


@pytest.mark.db
def test_finish_batch():
    batch = BatchFactory()
    with patch(
        'pd.groupon.models.game.signals.batch_finished'
    ) as mock_signal:
        finish_batch(batch.id)
        assert mock_signal.send.called
        assert mock_signal.send.call_args[0] == (batch,)
        assert batch.finish_status == BatchFinishStatus.done
        # the task should be idempotent
        finish_batch(batch.id)
        assert mock_signal.send.call_count == 1
        assert batch.finish_status == BatchFinishStatus.done


def test_close_payment_processing_orders(db_session, user, app):
    batch = BatchFactory()
    game = batch.create_game()
    db_session.commit()
    o = OrderFactory(game=game, user=user)
    signal('payment_created').send(Mock(object=o))

    batch.end_at = arrow.utcnow()
    batch.finish()
    db_session.commit()
    assert o.status == OrderStatus.payment_processing

    # 未到订单支付过期时间
    close_payment_processing_orders()
    assert o.status == OrderStatus.payment_processing

    # 订单支付过期时间已到
    # 假装批次过期是很久以前
    batch.end_at = arrow.utcnow().shift(
        seconds=-(app.config['PAYMENT_PROCESSING_ORDER_LINGER'] + 10000))
    db_session.commit()
    close_payment_processing_orders()
    assert o.status == OrderStatus.canceled
