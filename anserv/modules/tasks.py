from celery import task
from decorators import memoize_query
from mixpanel.mixpanel import EventTracker
import logging
from celery.task import periodic_task

log=logging.getLogger(__name__)

@task()
def track_event_mixpanel_batch(event_list):
    for list_start in xrange(0,len(event_list),50):
        event_tracker = EventTracker()
        event_tracker.track(event_list[list_start:(list_start+50)],event_list=True)

@memoize_query
#@periodic_task(run_every=2)
def foo():
    fs,db = get_db_and_fs_cron(foo)
    print "Test"

@memoize_query
#@periodic_task(run_every=10)
def foo2():
    fs,db = get_db_and_fs_cron(foo2)
    print "Another Test"

def get_db_and_fs_cron(f):
    import an_evt.views
    db = an_evt.views.get_database(f)
    fs = an_evt.views.get_filesystem(f)
    return fs,db


