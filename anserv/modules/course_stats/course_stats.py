from modules.decorators import view, query, event_handler, memoize_query
#from an_evt.models import StudentBookAccesses
from django.contrib.auth.models import User
from courseware.models import StudentModule
import json
from django.conf import settings
import dummy_values
import logging
from django.utils import timezone
import datetime

log=logging.getLogger(__name__)
import re

from mitxmako.shortcuts import render_to_response, render_to_string

@query('course', 'total_user_count')
def users_in_course_count_query(fs, db, course,params):
    return StudentModule.objects.filter(course_id=course).values('student').distinct().count()

@query('course', 'modules_accessed_count')
def modules_accessed_in_course_count_query(fs, db, course, params):
    return StudentModule.objects.filter(course_id=course).count()

@query('course', 'problems_tried_count')
def problems_tried_in_course_count_query(fs, db, course, params):
    return StudentModule.objects.filter(course_id=course,module_type="problem").count()

@query('course', 'video_watch_count)
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