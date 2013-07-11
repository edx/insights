"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import time, tempfile

from django.test import TestCase

from decorators import memoize_query,cron
from django.utils.timezone import timedelta
from celery.task import periodic_task


@cron(run_every=timedelta(seconds=1))
def test_cron_task(*args):
    """ Simple task that gets executed by the scheduler (celery beat).
        The test case test_cron verifies that the execution
        has taken place.

        Defined outside of the SimpleTest class because current support of celery decorators
        for methods and nested functions is experimental.
    """
    with open(tempfile.gettempdir() + '/' + 'test_cron_task_counter', 'a') as temp_file:
        temp_file.write(str(time.time()) + '\n') #write a timestamp for each call


@cron(run_every=timedelta(seconds=1))  # cron decorators should go on top
@memoize_query(60)
def test_cron_memoize_task(*args):
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

def run_celery_beat(seconds=3, verbose=False):
    """ Runs the task scheduler celery beat for the specified number of seconds as a child process
    """
    import os
    with open(os.devnull, 'w') as devnull:
        from subprocess import Popen
        command = ['python', 'manage.py',  'celery', 'worker', '-B', '--loglevel=INFO', '--settings=testsettings',]
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
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

    def __init__(self, arg):
        TestCase.__init__(self, arg)
        self.memoize_calls =  0


    def test_memoize(self):
        self.memoize_calls = 0
        return
        @memoize_query(0.05)
        def double_trouble(x):
            self.memoize_calls = self.memoize_calls + 1
            return 2*x

        self.assertEqual(double_trouble(2), 4)
        self.assertEqual(double_trouble(4), 8)
        self.assertEqual(double_trouble(2), 4)
        self.assertEqual(double_trouble(4), 8)
        self.assertEqual(self.memoize_calls, 2)
        time.sleep(0.1)
        self.assertEqual(double_trouble(2), 4)
        self.assertEqual(double_trouble(4), 8)
        self.assertEqual(double_trouble(2), 4)
        self.assertEqual(double_trouble(4), 8)
        self.assertEqual(self.memoize_calls, 4)

    def test_auth(self):
        ''' Inject a dummy settings.DJA_AUTH into auth. 
        '''
        import auth
        temp = auth.settings

        def plus1dec(f):
            def p1(x):
                return f(x)+1
            return p1

        def minus1dec(f):
            def p1(x):
                return f(x)-1
            return p1

        class S(object):
            DJA_AUTH = {'f1' : plus1dec, 
                        'g.*' : minus1dec}
        
        auth.settings = S
        
        @auth.auth
        def f1(x):
            return x**2
        
        @auth.auth
        def f2(x):
            return x**2

        @auth.auth
        def g2(x):
            return x**2

        self.assertEqual(f1(7), 50)
        self.assertEqual(f2(7), 49)
        self.assertEqual(g2(7), 48)

        auth.settings = temp
    
    def test_urls(self):
        ''' Simple test to make sure we're not throwing 500s. '''
        from django.test.client import Client
        c = Client()
        urls = ["/event_properties", "/schema"]
        for url in urls: 
            response = c.get(url)
            self.assertEqual(response.status_code, 200)

    def test_cron(self):
        """ Test that periodic tasks are scheduled and run
        """
        # truncate the file used as a counter of test_cron_task calls
        # the file is used to share state between the test process and
        # the scheduler process (celery beat)
        with open(tempfile.gettempdir() + '/' + 'test_cron_task_counter', 'w') as temp_file:
            pass

        run_celery_beat(seconds=3,verbose=False)

        # verify number of calls and time of last call
        with open(tempfile.gettempdir() + '/' + 'test_cron_task_counter', 'r') as temp_file:
            timestamps = temp_file.readlines()
            ncalls = len(timestamps)
            self.assertGreaterEqual(ncalls,2)
            last_call = float(timestamps[-1].rstrip())
            self.assertAlmostEqual(last_call, time.time(), delta=100)


    def test_cron_and_memoize(self):
        """ Test that periodic tasks are scheduled and run
        """

        # truncate the file used as a counter of test_cron_task calls
        # the file is used to share state between the test process and
        # the scheduler process (celery beat)
        with open(tempfile.gettempdir() + '/' + 'test_cron_memoize_task', 'w') as temp_file:
            pass

        run_celery_beat(seconds=3,verbose=False)

        # verify number of calls and time of last call
        with open(tempfile.gettempdir() + '/' + 'test_cron_memoize_task', 'r') as temp_file:
            timestamps = temp_file.readlines()
            ncalls = len(timestamps)
            self.assertEqual(ncalls,1)  # after the first call all subsequent calls should be cached
            last_call = float(timestamps[-1].rstrip())
            self.assertAlmostEqual(last_call, time.time(), delta=100)



