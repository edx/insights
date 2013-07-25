
import tempfile
import time

from django.test import TestCase
from django.test.client import Client
from django.core.cache import cache
from core.decorators import use_clearcache

def count_timestamps(tempfilename):
    with open(tempfile.gettempdir() + '/' + tempfilename, 'r') as temp_file:
        timestamps = temp_file.readlines()
        ncalls = len(timestamps)
        last_call = float(timestamps[-1].rstrip())
    return ncalls, last_call

def truncate_tempfile(tempfilename):
    """
     Truncates the file used to share state between the test process
     and the scheduler process (celery beat).
    """
    with open(tempfile.gettempdir() + '/' + tempfilename, 'w') as temp_file:
        pass

def run_celery_beat(seconds=3, verbose=False):
    """ Runs the task scheduler celery beat for the specified number of seconds as a child process
    """
    import os
    with open(os.devnull, 'w') as devnull:
        from subprocess import Popen
        command = ['python', 'manage.py',  'celery', 'worker', '-B', '--loglevel=INFO',]
        if verbose:
            suppress_output_args = {}
        else:
            suppress_output_args = {'stdout':devnull, 'stderr':devnull}

        celery_beat_process = Popen(command, **suppress_output_args)

        # give time to celery beat to execute test_cron_task
        from time import sleep
        print "running periodic tasks for %s seconds... " % seconds
        sleep(seconds)
        celery_beat_process.terminate()


class SimpleTest(TestCase):

    def __init__(self, arg):
        TestCase.__init__(self, arg)


    def test_cron(self):
        """ Test that periodic tasks are scheduled and run

        tests: tasks.test_cron_task
        """

        truncate_tempfile('test_cron_task_counter')
        run_celery_beat(seconds=3,verbose=False)

        # verify number of calls and time of last call
        ncalls, last_call = count_timestamps('test_cron_task_counter')
        self.assertGreaterEqual(ncalls, 2)
        self.assertAlmostEqual(last_call, time.time(), delta=100)


    def test_cron_and_memoize(self):
        """ Test that periodic tasks are scheduled and run, and the results
        are cached.

        tests: tasks.test_cron_memoize_task
        """
        truncate_tempfile('test_cron_memoize_task')

        # clear the cache from any previous executions of this test
        # cache.delete('test_cron_memoize_unique_cache_key')
        from tasks import test_cron_memoize_task

        use_clearcache(test_cron_memoize_task)()

        run_celery_beat(seconds=3,verbose=False)
        ncalls, last_call = count_timestamps('test_cron_memoize_task')
        self.assertEqual(ncalls,1)  # after the first call all subsequent calls should be cached
        self.assertAlmostEqual(last_call, time.time(), delta=100)

    def test_cron_and_memoize_and_view(self):
        """ Test that periodic tasks are scheduled, run, cached, and the
        cached results are available to @view

        tests: tasks.big_computation
        """

        truncate_tempfile('big_computation_counter')

        # delete cache from previous executions of this unit test
        from tasks import big_computation
        use_clearcache(big_computation)()

        run_celery_beat(seconds=3, verbose=False)

        ncalls_before, lastcall_before = count_timestamps('big_computation_counter')
        self.assertEqual(ncalls_before,1)  # after the first call all subsequent calls should be cached

        c = Client()
        status_code = c.get('/view/big_computation_visualizer').status_code
        content = c.get('/view/big_computation_visualizer').content
        self.assertEqual(status_code, 200)
        self.assertEqual(content, "<html>FAKERESULT</html>")

        # ensure big_computation was not called and the cached result was used
        # by the execution of c.get('/view...')
        ncalls_after, lastcall_after = count_timestamps('big_computation_counter')
        self.assertEqual(ncalls_before, ncalls_after)
        self.assertEqual(lastcall_before, lastcall_after)

    def test_cron_and_memoize_and_view_with_forcememoize(self):
        """ Test that periodic tasks are scheduled, run, and cached, and the
        cached results are available to @view. If the task is executed from
        the scheduler (as a periodic task) the computation should be redone and
        the new result should be stored in cache. If the task is executed from code
        (e.g. from a @view or @query handler) the result from cache should be returned.

        Tests task: tasks.big_computation_withfm
        """

        truncate_tempfile('big_computation_withfm_counter')

        from tasks import big_computation_withfm
        use_clearcache(big_computation_withfm)()

        run_celery_beat(seconds=3, verbose=False)
        ncalls_before, lastcall_before = count_timestamps('big_computation_withfm_counter')

        self.assertGreaterEqual(ncalls_before,2)
        self.assertAlmostEqual(lastcall_before, time.time(),delta=100)

        c = Client()
        status_code = c.get('/view/big_computation_visualizer_withfm').status_code
        content = c.get('/view/big_computation_visualizer_withfm').content
        self.assertEqual(status_code, 200)
        self.assertEqual(content, "<html>FAKERESULTFM</html>")

        ncalls_after, lastcall_after = count_timestamps('big_computation_withfm_counter')
        self.assertEqual(ncalls_before, ncalls_after)
        self.assertEqual(lastcall_before, lastcall_after)