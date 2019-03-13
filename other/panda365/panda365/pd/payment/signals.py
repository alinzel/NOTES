from blinker import signal


payment_created = signal(
    'payment_created',
    doc='支付创建. sender: payment'
)
payment_succeeded = signal(
    'payment_succeeded',
    doc='支付成功. sender: payment'
)
payment_failed = signal(
    'payment_failed',
    doc='支付失败. sender: payment'
)
payment_error = signal(
    'payment_error',
    doc='支付发生错误. sender: payment'
)
payment_canceled = signal(
    'payment_canceled',
    doc='用户取消支付. sender: payment'
)
