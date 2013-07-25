import tempfile
import time

from edinsights.core.decorators import memoize_query, cron
from django.utils.timezone import timedelta

def timestamp_to_tempfile(filename):
    with open(tempfile.gettempdir() + '/' + filename, 'a') as temp_file:
        temp_file.write(str(time.time()) + '\n') #write a timestamp for each call


# Test tasks are defined in tasks.py files. Other files could also be
# included using CELERY_IMPORTS. Avoid using @cron with nested functions and
# methods(the support of @periodic_task for these is experimental)
# The @cron decorator should precede all other decorators


@cron(run_every=timedelta(seconds=1))
def test_cron_task():
    """ Simple task that gets executed by the scheduler (celery beat).
        tested by: tests.SimpleTest.test_cron
    """

    timestamp_to_tempfile('test_cron_task_counter')


@cron(run_every=timedelta(seconds=1), force_memoize=False)  # cron decorators should go on top
@memoize_query(60)
def test_cron_memoize_task(fs):
    """
        Simple task that gets executed by the scheduler (celery beat).
        Combines periodic tasks and memoization, with force_memoize=False.
        This means that the periodic task will return cached results if possible.
        This scenario is probably not what you want.

        tested by: tests.SimpleTest.test_cron_and_memoize
    """

    timestamp_to_tempfile('test_cron_memoize_task')
    return 42


@cron(run_every=timedelta(seconds=1), force_memoize=False)  # cron decorators should go on top
@memoize_query(cache_time=60)
def big_computation():
    """
        Simple task that gets executed by the scheduler (celery beat) and also by @view

        Combines periodic tasks and memoization, with force_memoize=False.
        This means that the periodic task will return cached results if possible.
        This scenario is probably not what you want.

        tested by: tests.SimpleTest.test_cron_and_memoize_and_view
    """
    timestamp_to_tempfile('big_computation_counter')
    return "FAKERESULT"


@cron(run_every=timedelta(seconds=1), force_memoize=True)  # cron decorators should go on top
@memoize_query(cache_time=60)
def big_computation_withfm():
    """
     Simple task that gets executed by the scheduler (celery beat) and also by @view
     Combines periodic tasks and memoization, with force_memoize=True.
     This means that the task will redo the computation regardless of
     whether the result was already in the cache when it is called from the
     task scheduler. If the task is called from code, it will return the cached
     result.  This scenario is probably what you want.

     tested by: tests.SimpleTest.test_cron_and_memoize_and_view_with_forcememoize
    """
    timestamp_to_tempfile('big_computation_withfm_counter')
    return "FAKERESULTFM"

# TODO put every task in its own file, and use CELERY_IMPORTS to run
# individual tasks instead of all tasks at the same time for each test
