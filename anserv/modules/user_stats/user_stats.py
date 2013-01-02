from modules.decorators import view, query, event_handler, cron
#from an_evt.models import StudentBookAccesses
from django.contrib.auth.models import User
from courseware.models import StudentModule

@cron(1)
def foo(db, params):
    print "Test"

@view(name = 'user_count')
def total_user_count_view(db, params):
    return "The system has "+str(total_user_count_query(db, params)) + " users total"

@view(name = 'course_enrollment')
def total_course_enrollment(db,params):
    # SELECT course_id,COUNT(DISTINCT user_id) AS students FROM student_courseenrollment GROUP BY course_id;
    return "Unimplemented"

@view(name = 'active_students')
def active_course_enrollment(db,params):
    # SELECT course_id,COUNT(DISTINCT student_id) FROM `courseware_studentmodule` WHERE DATE(modified) >= DATE(DATE_ADD(NOW(), INTERVAL -7 DAY)) GROUP BY course_id
    return "Unimplemented"

@view(name = 'active_plot')
def active_user_plot(db, params):
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
    

