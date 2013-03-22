from celery import task
from decorators import memoize_query, query
from mixpanel.mixpanel import EventTracker
import logging
from celery.task import periodic_task
from modules import common
from django.conf import settings
import sys
import io

sys.path.append(settings.DJANGOAPPS_PATH)
sys.path.append(settings.COMMON_PATH)
sys.path.append(settings.LMS_LIB_PATH)

import courseware
from courseware import grades
from courseware.models import StudentModule
from courseware.courses import get_course_with_access
from courseware.model_data import ModelDataCache, LmsKeyValueStore
from django.contrib.auth.models import User
import re
import csv
from django.http import HttpResponse
import json


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

@task
def get_student_course_stats(request, course):
    course_obj = get_course_with_access(request.user, course, 'load', depth=None)
    users_in_course = StudentModule.objects.filter(course_id=course).values('student').distinct()
    users_in_course_ids = [u['student'] for u in users_in_course]
    log.debug("Users in course {0}".format(users_in_course))
    courseware_summaries = []
    rows = []
    for user in users_in_course_ids:
        student = User.objects.get(id=int(user))
        log.debug(student)
        # NOTE: To make sure impersonation by instructor works, use
        # student instead of request.user in the rest of the function.

        # The pre-fetching of groups is done to make auth checks not require an
        # additional DB lookup (this kills the Progress page in particular).
        student = User.objects.prefetch_related("groups").get(id=student.id)

        model_data_cache = None

        #courseware_summary = grades.progress_summary(student, request, course_obj, model_data_cache)
        grade_summary = grades.grade(student, request, course_obj, model_data_cache)
        courseware_summaries.append(grade_summary)
    for z in xrange(0,len(courseware_summaries)):
        log.debug(courseware_summaries[z])
        row = {'student' : users_in_course_ids[z], 'overall_percent' : courseware_summaries[z]["percent"]}
        row.update({c['category'] : c['percent'] for c in courseware_summaries[z]["grade_breakdown"]})
        rows.append(row)
    return json.dumps(rows)

