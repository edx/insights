
import tempfile
import time

from django.core.cache import cache
from edinsights.core.decorators import memoize_query, cron
from django.utils.timezone import timedelta

def timestamp_to_tempfile(filename):
    with open(tempfile.gettempdir() + '/' + filename, 'a') as temp_file:
        temp_file.write(str(time.time()) + '\n') #write a timestamp for each call

@cron(run_every=timedelta(seconds=1))
def test_cron_task(params={}):
    """ Simple task that gets executed by the scheduler (celery beat).
        The test case test_cron verifies that the execution
        has taken place.

        Defined outside of the SimpleTest class because current support of celery decorators
        for methods and nested functions is experimental.
    """
    timestamp_to_tempfile('test_cron_task_counter')


@cron(run_every=timedelta(seconds=1), force_memoize=False)  # cron decorators should go on top
@memoize_query(60, key_override='test_cron_memoize_unique_cache_key')
def test_cron_memoize_task():
    """ Simple task that gets executed by the scheduler (celery beat).
        The test case test_cron_and_memoize verifies that the execution
        has taken place.

        Defined outside of the SimpleTest class because current support of celery decorators
        for methods and nested functions is experimental.

        The cron decorator should precede all other decorators
    """
    timestamp_to_tempfile('test_cron_memoize_task')
    return 42


@cron(run_every=timedelta(seconds=1), force_memoize=False)  # cron decorators should go on top
@memoize_query(cache_time=60, key_override='big_computation_key')
def big_computation():
    """
    Combines periodic tasks and memoization, with force_memoize=False.
    This means that the periodic task will return cached results if possible.
    This scenario is probably not what you want.
    """
    timestamp_to_tempfile('big_computation_counter')
    return "FAKERESULT"


@cron(run_every=timedelta(seconds=1), force_memoize=True)  # cron decorators should go on top
@memoize_query(cache_time=60, key_override='big_computation_key_withfm')
def big_computation_withfm():
    """
     Combines periodic tasks and memoization, with force_memoize=True.
     This means that the task will redo the computation regardless of
     whether the result was already in the cache when it is called from the
     task scheduler. If the task is called from code, it will return the cached
     result.  This scenario is probably what you want.
    """
    timestamp_to_tempfile('big_computation_withfm_counter')
    return "FAKERESULTFM"
