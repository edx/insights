from celery import task
from modules.decorators import memoize_query, query
from modules.mixpanel.mixpanel import EventTracker
import logging
from celery.task import periodic_task
from modules import common
from django.conf import settings
import sys
import io
from dateutil import parser
import os

log=logging.getLogger(__name__)

#sys.path += settings.MITX_LIB_PATHS
#sys.path = [p for p in sys.path if p!=settings.MITX_LIBRARY_PATH]
import imp

def import_custom_module(name):
    f, pathname, desc = imp.find_module(name, sys.path[1:])
    return imp.load_module(name, f, pathname, desc)

#If we are importing the MITx modules, then full functionality will be enabled here.
if settings.IMPORT_MITX_MODULES:
    from courseware import grades
    from courseware.courses import get_course_with_access
    from courseware.model_data import ModelDataCache, LmsKeyValueStore

#If not, we will retain the studentmodule, which will give minimal functionality
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

#Locks are set by long-running tasks to ensure that they are not duplicated.
LOCK_EXPIRE = 24 * 60 * 60 # 1 day

class RequestDict(object):
    """
    Mocks the request object.  Needed for the MITx grading functions to work.
    """
    def __init__(self, user):
        self.META = {}
        self.POST = {}
        self.GET = {}
        self.user = user
        self.path = None

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

@periodic_task(run_every=settings.TIME_BETWEEN_DATA_REGENERATION, name="tasks.regenerate_student_course_data")
def regenerate_student_course_data():
    """
    Generates the data for a given student's performance in a course.
    This function is a periodic task (cron job) that runs at a specified interval,
    pulls a list of courses, and for each course sends messages to the appropriate tasks.
    """
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

@task(name="tasks.get_student_course_stats")
def get_student_course_stats(request, course):
    """
    Regenerates student stats for a course (weighted section grades)
    Stores the grades to a mongo (json) collection, and to csv files
    request - a mock request (using RequestDict)
    course - a string course id
    """
    course_name = re.sub("[/:]","_",course)
    log.info(course_name)
    lock_id = "regenerate_student_course_data-lock-{0}-{1}-{2}".format(course,"student_course_grades", course_name)
    log.info(lock_id)
    acquire_lock = lambda: cache.add(lock_id, "true", LOCK_EXPIRE)
    release_lock = lambda: cache.delete(lock_id)
    if acquire_lock():
        try:
            fs, db = get_db_and_fs_cron(get_student_course_stats)
            collection = db['student_course_stats']
            courseware_summaries, users_in_course_ids = get_student_course_stats_base(request,course, "grades")
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
        return json.dumps({'result_data' : rows, 'result_file' : "{0}/{1}".format(settings.PROTECTED_DATA_URL, file_name)})
    return {}

@task(name="tasks.get_student_problem_stats")
def get_student_problem_stats(request,course):
    """
    Regenerates student stats for a course (unweighted exercise grades)
    Stores the grades to a mongo (json) collection, and to csv files
    request - a mock request (using RequestDict)
    course - a string course id
    """
    course_name = re.sub("[/:]","_",course)
    log.info(course_name)
    lock_id = "regenerate_student_course_data-lock-{0}-{1}-{2}".format(course,"student_problem_grades", course_name)
    log.info(lock_id)
    acquire_lock = lambda: cache.add(lock_id, "true", LOCK_EXPIRE)
    release_lock = lambda: cache.delete(lock_id)
    if acquire_lock():
        try:
            fs, db = get_db_and_fs_cron(get_student_course_stats)
            collection = db['student_problem_stats']
            courseware_summaries, users_in_course_ids = get_student_course_stats_base(request,course, "grades")
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
        return json.dumps({'result_data' : rows, 'result_file' : "{0}/{1}".format(settings.PROTECTED_DATA_URL, file_name)})
    return {}

def get_student_course_stats_base(request,course, type="grades"):
    """
    Called by get_student_course_stats and get_student_problem_stats
    Gets a list of users in a course, and then computes grades for them
    request - a mock request (using RequestDict)
    course - a string course id
    type - whether to get student weighted grades or unweighted grades.  If "grades" will get weighted
    """
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
    """
    Given a filesystem and a list of results, will write the results to a file
    fs - filesystem object
    filename - the name of the csv file to write
    results - a list of dictionaries
    """
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
    """
    Given a collection and results, writes the results to the collection
    collection - a mongo collection
    results - a list of dictionaries
    course - string course id
    """
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

#Used by regenerate_student_course_data to find and call tasks
STUDENT_TASK_TYPES = {
    'course' : get_student_course_stats,
    'problem' : get_student_problem_stats
}