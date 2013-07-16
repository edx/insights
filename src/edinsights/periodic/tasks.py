
import tempfile
import time

from django.core.cache import cache
from edinsights.core.decorators import memoize_query, cron
from django.utils.timezone import timedelta

@cron(run_every=timedelta(seconds=1))
def test_cron_task():
    """ Simple task that gets executed by the scheduler (celery beat).
        The test case test_cron verifies that the execution
        has taken place.

        Defined outside of the SimpleTest class because current support of celery decorators
        for methods and nested functions is experimental.
    """
    with open(tempfile.gettempdir() + '/' + 'test_cron_task_counter', 'a') as temp_file:
        temp_file.write(str(time.time()) + '\n') #write a timestamp for each call


@cron(run_every=timedelta(seconds=1))  # cron decorators should go on top
@memoize_query(60, key_override='test_cron_memoize_unique_cache_key')
def test_cron_memoize_task():
    """ Simple task that gets executed by the scheduler (celery beat).
        The test case test_cron_and_memoize verifies that the execution
        has taken place.

        Defined outside of the SimpleTest class because current support of celery decorators
        for methods and nested functions is experimental.

        The cron decorator should precede all other decorators
    """

    with open(tempfile.gettempdir() + '/' + 'test_cron_memoize_task', 'a') as temp_file:
        temp_file.write(str(time.time()) + '\n') #write a timestamp for each call

    return 42

@cron(run_every=timedelta(seconds=1))  # cron decorators should go on top
@memoize_query(cache_time=60, key_override='big_computation_key')
def big_computation():
    # time.sleep(seconds=10)

    with open(tempfile.gettempdir() + '/' + 'big_computation_counter', 'a') as temp_file:
        temp_file.write(str(time.time()) + '\n') #write a timestamp for each call

    return "FAKERESULT"