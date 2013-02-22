from celery import task
from decorators import memoize_query, query
from mixpanel.mixpanel import EventTracker
import logging
from celery.task import periodic_task
from modules import common

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

@periodic_task(run_every=5*60*60)
@query(name = 'active_students', category = 'global')
def active_course_enrollment_query(fs, db, params):
    r = common.query_results("SELECT course_id,COUNT(DISTINCT student_id) FROM `courseware_studentmodule` WHERE DATE(modified) >= DATE(DATE_ADD(NOW(), INTERVAL -7 DAY)) GROUP BY course_id;")
    return r

def get_db_and_fs_cron(f):
    import an_evt.views
    db = an_evt.views.get_database(f)
    fs = an_evt.views.get_filesystem(f)
    return fs,db


