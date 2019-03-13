import arrow
from flask import current_app
from pd.sqla import db, logger
from pd.groupon.models.game import Batch, BatchFinishStatus
from pd.groupon.models.order import Order, OrderStatus
from pd.tasks import celery_app


@celery_app.task
def check_for_imminent_batches():
    """
    找出即将结束的批次，安排它们在end_at进行finish
    """
    next_tick = arrow.utcnow().shift(
        seconds=celery_app.visibility_timeout,
    )
    for batch in Batch.query.filter(
        Batch.finish_status == BatchFinishStatus.pending,
        Batch.end_at <= next_tick,
    ):
        finish_batch.apply_async(
            kwargs=dict(batch_id=batch.id),
            eta=batch.end_at,
        )
        batch.finish_status = BatchFinishStatus.scheduled
        db.session.commit()
        logger.info(
            'scheduled finish task for batch %d at %s',
            batch.id, batch.end_at,
        )


@celery_app.task
def finish_batch(batch_id):
    batch = Batch.query.get(batch_id)
    batch.finish()
    db.session.commit()


@celery_app.task
def close_payment_processing_orders():
    """
    若订单在其批次结束后一段时间仍未支付成功，则将其设为取消
    """
    oids = [r.id for r in db.session.query(Order.id).join(Order.batch).filter(
        # Batch.is_running.isnot(False),
        Order.status == OrderStatus.payment_processing,
        Order.updated_at > (
            Batch.end_at + db.text(
                "'{} seconds'".format(
                    current_app.config['PAYMENT_PROCESSING_ORDER_LINGER']
                )
            )
        ),
    )]
    if oids:
        Order.query.filter(
            Order.id.in_(oids)
        ).update({
            Order.status: OrderStatus.canceled,
        }, synchronize_session=False)
        db.session.commit()
        logger.info(
            'orders closed because they are not paid %d seconds after their '
            'batches end', oids
        )
