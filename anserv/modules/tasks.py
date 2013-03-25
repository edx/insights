from celery import task
from decorators import memoize_query, query
from mixpanel.mixpanel import EventTracker
import logging
from celery.task import periodic_task
from modules import common
from django.conf import settings
import sys
import io
from dateutil import parser

log=logging.getLogger(__name__)

if settings.IMPORT_MITX_MODULES:
    sys.path.append(settings.DJANGOAPPS_PATH)
    sys.path.append(settings.COMMON_PATH)
    sys.path.append(settings.LMS_LIB_PATH)

    from courseware import grades
    from courseware.models import StudentModule
    from courseware.courses import get_course_with_access
    from courseware.model_data import ModelDataCache, LmsKeyValueStore
else:
    import courseware_old as courseware
    from courseware.models import StudentModule

from django.contrib.auth.models import User
import re
import csv
from django.http import HttpResponse
import json
from celery import current_task
import datetime
from django.utils.timezone import utc
from django.core.cache import cache
import time

LOCK_EXPIRE = 24 * 60 * 60 # 1 day

class RequestDict(object):
    def __init__(self, user):
        self.META = {}
        self.POST = {}
        self.GET = {}
        self.user = user
        self.path = None

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

@periodic_task(run_every=datetime.timedelta(days=1))
def regenerate_student_course_data():
    if not settings.IMPORT_MITX_MODULES:
        log.error("Cannot import mitx modules and thus cannot regenerate student course data.")
        return
    log.debug("Regenerating course data.")
    user = User.objects.all()[0]
    request = RequestDict(user)
    all_courses = [c['course_id'] for c in StudentModule.objects.values('course_id').distinct()]
    all_courses = list(set(all_courses))
    log.debug(all_courses)
    for course in all_courses:
        for type in ['course', 'problem']:
            STUDENT_TASK_TYPES[type].delay(request,course)

@task
def get_student_course_stats(request, course):
    course_name = re.sub("[/:]","_",course)
    lock_id = "regenerate_student_course_data-lock-{0}-{1}-{2}".format(course,"student_course_grades", course_name)
    acquire_lock = lambda: cache.add(lock_id, "true", LOCK_EXPIRE)
    release_lock = lambda: cache.delete(lock_id)
    if acquire_lock():
        try:
            log.debug(lock_id)
            fs, db = get_db_and_fs_cron(get_student_course_stats)
            collection = db['student_course_stats']
            courseware_summaries, users_in_course_ids = get_student_course_stats_base(request,course,course_name, "grades")
            rows = []
            for z in xrange(0,len(courseware_summaries)):
                row = {'student' : users_in_course_ids[z], 'overall_percent' : courseware_summaries[z]["percent"]}
                row.update({c['category'] : c['percent'] for c in courseware_summaries[z]["grade_breakdown"]})
                rows.append(row)

            file_name = "student_grades_{0}.csv".format(course_name)
            try:
                return_csv(fs,file_name, rows)
            except:
                log.exception("Could not generate csv file.")
                file_name = "no_file_generated"
            write_to_collection(collection, rows, course)
        finally:
            release_lock()
        return json.dumps({'result_data' : rows, 'result_file' : "{0}/{1}".format(settings.STATIC_URL, file_name)})
    return {}

@task
def get_student_problem_stats(request,course):
    course_name = re.sub("[/:]","_",course)
    lock_id = "regenerate_student_course_data-lock-{0}-{1}-{2}".format(course,"student_problem_grades", course_name)
    acquire_lock = lambda: cache.add(lock_id, "true", LOCK_EXPIRE)
    release_lock = lambda: cache.delete(lock_id)
    if acquire_lock():
        try:
            log.debug(lock_id)
            fs, db = get_db_and_fs_cron(get_student_course_stats)
            collection = db['student_problem_stats']
            courseware_summaries, users_in_course_ids = get_student_course_stats_base(request,course,course_name, "grades")
            rows = []
            for z in xrange(0,len(courseware_summaries)):
                log.info(courseware_summaries[z])
                row = {'student' : users_in_course_ids[z]}
                #row.update({'problem_data' : courseware_summaries[z]})
                row.update({c['label'] : c['percent'] for c in courseware_summaries[z]["section_breakdown"]})
                rows.append(row)

            file_name = "student_problem_grades_{0}.csv".format(course_name)
            try:
                return_csv(fs,file_name, rows)
            except:
                log.exception("Could not generate csv file.")
                file_name = "no_file_generated"
            write_to_collection(collection, rows, course)
        finally:
            release_lock()
        return json.dumps({'result_data' : rows, 'result_file' : "{0}/{1}".format(settings.STATIC_URL, file_name)})
    return {}

def get_student_course_stats_base(request,course,course_name, type="grades"):
    fs, db = get_db_and_fs_cron(get_student_course_stats)
    course_obj = get_course_with_access(request.user, course, 'load', depth=None)
    users_in_course = StudentModule.objects.filter(course_id=course).values('student').distinct()
    users_in_course_ids = [u['student'] for u in users_in_course]
    log.debug("Users in course count: {0}".format(len(users_in_course_ids)))
    courseware_summaries = []
    for i in xrange(0,len(users_in_course_ids)):
        try:
            user = users_in_course_ids[i]
            current_task.update_state(state='PROGRESS', meta={'current': i, 'total': len(users_in_course_ids)})
            student = User.objects.using('default').prefetch_related("groups").get(id=int(user))

            model_data_cache = None

            if type=="grades":
                grade_summary = grades.grade(student, request, course_obj, model_data_cache)
            else:
                grade_summary = grades.progress_summary(student, request, course_obj, model_data_cache)
            courseware_summaries.append(grade_summary)
        except:
            log.exception("Could not generate data for {0}".format(users_in_course_ids[i]))
    return courseware_summaries, users_in_course_ids

def return_csv(fs, filename, results):
    if len(results)<1:
        return
    output = fs.open(filename, 'w')
    writer = csv.writer(output, dialect='excel', quotechar='"', quoting=csv.QUOTE_ALL)
    row_keys = results[0].keys()
    writer.writerow(row_keys)
    for datarow in results:
        encoded_row = []
        for key in row_keys:
            encoded_row+=[unicode(datarow[key]).encode('utf-8')]
        writer.writerow(encoded_row)
    output.close()
    return True

def write_to_collection(collection, results, course):
    if len(results)<1:
        return
    now = datetime.datetime.utcnow().replace(tzinfo=utc)
    now_string = str(now)
    mongo_results = {'updated' : now_string, 'course' : course, 'results' : results}
    sba = list(collection.find({'course' : course}))
    if len(sba)>0:
        collection.update({'course':course}, mongo_results, True)
    else:
        collection.insert(mongo_results)

STUDENT_TASK_TYPES = {
    'course' : get_student_course_stats,
    'problem' : get_student_problem_stats
}


