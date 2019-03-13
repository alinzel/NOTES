from unittest.mock import Mock, patch
from pd.tasks import monitoring as m


def test_datadog_events():
    class Foo:
        pass
    sender = Foo()
    sender.__name__ = 'echo_task'

    with patch('pd.tasks.monitoring.statsd') as mock_statsd:
        m.count_processed(sender)
        # should track state if given
        m.count_processed(sender, state='blah')
        assert 'blah' in str(mock_statsd.increment.call_args)
        sender._stats_timer = Mock()
        # should stop the timer if one exists
        m.count_processed(sender)
        assert sender._stats_timer.stop.called
        m.count_queued(sender)
        m.start_task_timer(sender)
