from celery import task
from decorators import cron_new, memoize_query
from mixpanel.mixpanel import EventTracker
import logging

log=logging.getLogger(__name__)

@task()
def track_event_mixpanel_batch(event_list):
    for list_start in xrange(0,len(event_list),50):
        event_tracker = EventTracker()
        event_tracker.track(event_list[list_start:(list_start+50)],event_list=True)

@memoize_query
@cron_new(2)
def foo(fs, db,params):
    print "Test"

@memoize_query
@cron_new(2)
def foo2(fs, db,params):
    print "Another Test"


