from modules.decorators import view, query, event_handler
from an_evt.models import StudentBookAccesses
from django.contrib.auth.models import User

@view(name = 'user_count')
def total_user_count_view(db, params):
    return "The system has "+str(total_user_count_query(db, params)) + " users total"

@query('global', 'total_user_count')
def total_user_count_query(db, params):
    return User.objects.count()

@query('global', 'enrolled_user_count')
def enrolled_user_count_query(db, params):
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
    queries.append("select registrations, count(registrations) from (select count(user_id) as registrations from student_courseenrollment group by user_id) as registrations_per_user group by registrations;")
    

