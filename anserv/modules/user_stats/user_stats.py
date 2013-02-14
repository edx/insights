from modules.decorators import view, query, event_handler, memoize_query, cron
#from an_evt.models import StudentBookAccesses
from django.contrib.auth.models import User
from courseware.models import StudentModule
import json
from django.conf import settings
import dummy_values
import logging

log=logging.getLogger(__name__)
import re

from mitxmako.shortcuts import render_to_response, render_to_string

@memoize_query
@cron(time = 2)
def foo(db,params):
    print "Test"

@view(name = 'user_count', category = 'global', args=[])
@memoize_query(cache_time=1)
def total_user_count_view():
    return "The system has "+str(total_user_count_query()) + " users total"

@query('global', 'total_user_count')
def total_user_count_query():
    return User.objects.count()

@view(name = 'course_enrollment')
def total_course_enrollment(fs, db,params):
    data = total_course_enrollment_query(fs, db, params)
    course_enrollment_unis = []
    course_enrollment_courses = { }
    course_enrollment_terms = { };
    course_enrollment_courses_by_term = { };
    course_enrollment_terms_by_course = { };
    for i in range(0, len(data['course_id'])):
        mch = re.search('^(.*?)\/(.*?)\/(.*?)$', data['course_id'][i])
        uni = mch.group(1)
        course = mch.group(2)
        term = mch.group(3)
        if not uni in course_enrollment_unis:
            course_enrollment_unis.append(uni)
            course_enrollment_courses[uni] = []
            course_enrollment_terms[uni] = []
            course_enrollment_courses_by_term[uni] = { }
            course_enrollment_terms_by_course[uni] = { }
        if not course in course_enrollment_courses[uni]:
            course_enrollment_courses[uni].append(course)
            if not term in course_enrollment_terms[uni]:
                course_enrollment_terms[uni].append(term)
                if not term in course_enrollment_courses_by_term[uni]:
                    course_enrollment_courses_by_term[uni][term] = {}
                    course_enrollment_courses_by_term[uni][term][course] = data['students'][i]
                if not course in course_enrollment_terms_by_course[uni]:
                    course_enrollment_terms_by_course[uni][course] = {}
                    course_enrollment_terms_by_course[uni][course][term] = data['students'][i]
                  
    return render_to_response('user_stats_course_enrollment.html', { 'unis': course_enrollment_unis, 'courses': course_enrollment_courses, 'terms': course_enrollment_terms, 'courses_by_term': course_enrollment_courses_by_term, 'terms_by_course': course_enrollment_terms_by_course })
    #return json.dumps(total_course_enrollment_query(fs, db, params), indent=2)

@query(name = 'course_enrollment')
def total_course_enrollment_query(fs, db, params):
    r = query_results("SELECT course_id,COUNT(DISTINCT user_id) AS students FROM student_courseenrollment GROUP BY course_id;")
    return r

@view(name = 'active_students')
def active_course_enrollment_view(fs, db,params):
    ''' Student who were active in the course in the past week
    '''
    ''' UNTESTED '''
    return json.dumps(active_course_enrollment_query(fs, db, params), indent=2)

@query(name = 'active_students', category = 'global')
@memoize_query(cache_time=15*60)
def active_course_enrollment_query(fs, db, params):
    r = query_results("SELECT course_id,COUNT(DISTINCT student_id) FROM `courseware_studentmodule` WHERE DATE(modified) >= DATE(DATE_ADD(NOW(), INTERVAL -7 DAY)) GROUP BY course_id;")
    return r

@view(name = 'active_plot')
def active_user_plot(fs, db, params):
    return "Unimplemented"
    u=list(User.objects.all())
    ul = u[:200]

    # A list where, for each user, we have date joined and date of last access
    dicts = [{'id':u.id,'joined':u.date_joined, 'left':StudentModule.objects.filter(student=u.id).order_by('modified').reverse()[:1]} for u in ul]
    dicts=[d for d in dicts if len(d['left'])!=0]
    for i in range(len(dicts)):
        dicts[i]['lastseen']=dicts[i]['left'][0].modified

    def count_students(day):
        ''' Helper function to count number of students active on a given day '''
        return len([d for d in dicts2 if d['joined']<day and d['lastseen']>day])

#### IN PROGRESS

def query_results(query):
    from django.db import connection
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        desc = [d[0] for d in cursor.description] # Names of table columns
        results = zip(*cursor.fetchall()) # Results for each column
        return dict(zip(desc, results))
    except:
        log.error("Could not execute query {0}".format(query))
        return {}

@query('global', 'enrolled_user_count')
def enrolled_user_count_query(fs, db, params):
    queries=[]
    queries.append("select count(distinct user_id) as unique_students from student_courseenrollment;")
    from django.db import connection
    cursor = connection.cursor()
    results =[]
    for query in queries:
        cursor.execute(query)
        results.append(dictfetchall(cursor))

    return results

@query('global', 'per_course_user_count')
def per_course_user_count():
    queries.append("select count(user_id) as students, course_id from student_courseenrollment group by course_id order by students desc;")

@query('global', 'course_enrollment_histogram')
def course_enrollment_histogram():
    queries.append("select registrations, count(registrations) from (select count(user_id) as registrations from student_courseenrollment group by user_id) as registrations_per_user group by registrations;")


if settings.DUMMY_MODE:
    from dummy_values import *
