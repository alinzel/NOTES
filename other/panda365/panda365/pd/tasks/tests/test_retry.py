from celery import Celery
from celery.exceptions import Retry
import requests
import requests_mock
import pytest

from pd.tasks.retry import retriable, requests_retriable

# TODO: 用celery提供的pytest fixture重构测试
# 需要在这个issue修复后进行: https://github.com/celery/celery/issues/3642


@pytest.fixture
def celery(clean_redis):
    # TODO 可用celery_app、celery_wroker 等celery4提供的fixture来替换
    # TODO 但celery_worker目前版本还有bug:https://github.com/celery/celery/issues/3642
    c = Celery()
    c.conf.task_always_eager = True
    c.conf.task_eager_propagates = True
    return c


def test_retry(celery):
    max_retries = 3

    @celery.task(bind=True)
    @retriable([ValueError], max_retries=max_retries, delay=0)
    def get_item(self):
        if self.request.retries < max_retries:
            raise ValueError(self.request.retries)
        return self.request.retries

    # in eager mode retry is raised even if the task finally succeeds
    with pytest.raises(Retry) as exc_info:
        get_item.delay()

    # retried 1 time less than max_retries
    assert exc_info.value.args[1].args[0] == max_retries - 1


@pytest.mark.parametrize('retriable_status_codes, should_retry', [
    [None, False],  # should not retry on HTTP error
    [[403], False],  # should retry on HTTP error if code is not retry-able
    [[502], True],  # 502 can be retried later :)
])
def test_requests_retriable(celery, retriable_status_codes, should_retry):

    url = 'http://fake.com'

    @celery.task
    @requests_retriable(status_codes=retriable_status_codes, max_retries=1)
    def get_item(u):
        resp = requests.get(u)
        resp.raise_for_status()
        return resp  # pragma: no cover

    with requests_mock.Mocker() as m:
        m.get(url, status_code=502)
        with pytest.raises(requests.HTTPError):
            get_item.delay(url)
        assert m.call_count == 2 if should_retry else 1
