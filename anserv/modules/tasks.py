"""
This module has examples periodic tasks (akin to cron) and normal tasks (delayed jobs).
It can also contain global tasks.
"""

from celery import task
from decorators import memoize_query, query
from mixpanel.mixpanel import EventTracker
import logging
from celery.task import periodic_task
from modules import common
import datetime

log=logging.getLogger(__name__)

@task()
def track_event_mixpanel_batch(event_list):
    """
    An example of a task.  This will take in a list of events and stream them to mixpanel.
    Tasks run as delayed jobs, and are processed by celery workers running on the backend.
    """
    for list_start in xrange(0,len(event_list),50):
        event_tracker = EventTracker()
        event_tracker.track(event_list[list_start:(list_start+50)],event_list=True)

@memoize_query
#@periodic_task(run_every=2)
def foo():
    """
    An example of a periodic task.  Uncomment the periodic_task decorator to run this every 10 seconds.
    """
    fs,db = get_db_and_fs_cron(foo)
    print "Test"

@memoize_query
#@periodic_task(run_every=datetime.timedelta(seconds=10))
def foo2():
    """
    An example of a periodic task.  Uncomment the periodic_task decorator to run this every 10 seconds.
    """
    fs,db = get_db_and_fs_cron(foo2)
    print "Another Test"

def get_db_and_fs_cron(f):
    """
    Gets the correct fs and db for a given input function
    f - a function signature
    fs - A filesystem object
    db - A mongo database collection
    """
    import an_evt.views
    db = an_evt.views.get_database(f)
    fs = an_evt.views.get_filesystem(f)
    return fs,db

