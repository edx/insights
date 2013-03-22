from modules.decorators import view, query, event_handler, memoize_query
#from an_evt.models import StudentBookAccesses
from django.contrib.auth.models import User

import json
from django.conf import settings
import logging
from django.utils import timezone
import datetime
from modules import common
import sys
from django.contrib.auth.models import User

log=logging.getLogger(__name__)
import re
import os

log.debug(settings.MITX_PATH)

sys.path.append(settings.DJANGOAPPS_PATH)
sys.path.append(settings.COMMON_PATH)
sys.path.append(settings.LMS_LIB_PATH)

#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lms.ens.dev")
import courseware
from courseware import grades
from courseware.models import StudentModule
from courseware.courses import get_course_with_access
from courseware.model_data import ModelDataCache, LmsKeyValueStore

from mitxmako.shortcuts import render_to_response, render_to_string

@query('course', 'total_user_count')
def users_in_course_count_query(fs, db, course,params):
    return users_in_course_query(fs,db,course,params).count()

@query('course', 'all_users')
def users_in_course_query(fs, db, course,params):
    return StudentModule.objects.filter(course_id=course).values('student').distinct()

@query('course', 'modules_accessed_count')
def modules_accessed_in_course_count_query(fs, db, course, params):
    return StudentModule.objects.filter(course_id=course).count()

@query('course', 'problems_tried_count')
def problems_tried_in_course_count_query(fs, db, course, params):
    return StudentModule.objects.filter(course_id=course,module_type="problem").count()

@query('course', 'video_watch_count')
def videos_watched_in_course_count_query(fs, db, course, params):
    return StudentModule.objects.filter(course_id=course,module_type="video").count()

@view('course', 'total_user_count')
def users_in_course_count_view(fs, db, course, params):
    return "The system has "+str(users_in_course_count_query(fs,db,course,params)) + " users total"

@view('course', 'modules_accessed_count')
def modules_accessed_in_course_count_view(fs, db, course, params):
    return str(modules_accessed_in_course_count_query(fs,db,course,params)) + " modules accessed in the course."

@view('course', 'problems_tried_count')
def problems_tried_in_course_count_view(fs, db, course, params):
    return str(problems_tried_in_course_count_query(fs,db,course,params)) + " problems tried in the course."

@view('course', 'video_watch_count')
def videos_watched_in_course_count_view(fs, db, course, params):
    return str(videos_watched_in_course_count_query(fs,db,course,params)) + "videos watched in the course."

@query('global', 'users_per_course_count')
def users_per_course_count_query():
    query_string = "SELECT course_id, COUNT(DISTINCT user_id) AS count FROM student_courseenrollment GROUP BY course_id"
    return common.query_results(query_string)

@view('global', 'users_per_course')
def users_per_course_count_view():
    query_data = users_per_course_count_query()
    return common.render_query_as_table(query_data)

@query('global', 'new_students')
@memoize_query(cache_time=15*60)
def new_course_enrollment_query(fs, db, params):
    r = common.query_results("SELECT course_id,COUNT(DISTINCT student_id) FROM `courseware_studentmodule` WHERE DATE(created) >= DATE(DATE_ADD(NOW(), INTERVAL -7 DAY)) GROUP BY course_id;")
    return r

@view('global', 'new_students')
def new_course_enrollment_view(fs, db, params):
    r = new_course_enrollment_query(fs,db,params)
    return common.render_query_as_table(r)

@query('course', 'student_grades')
def course_grades_query(fs,db,course, params):
    request = params['request']
    course_obj = get_course_with_access(request.user, course, 'load', depth=None)
    users_in_course = users_in_course_query(fs,db,course,params)
    users_in_course_ids = [u['student'] for u in users_in_course]
    log.debug("Users in course {0}".format(users_in_course))
    courseware_summaries = []
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
    return courseware_summaries

