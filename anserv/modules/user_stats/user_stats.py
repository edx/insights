from modules.decorators import view, query, event_handler
from an_evt.models import StudentBookAccesses
from django.contrib.auth.models import User

@view('global', 'user_count')
def total_user_count_view(db, params):
    return "The system has "+str(total_user_count_query(db, params)) + " users total"

@query('global', 'user_count')
def total_user_count_query(db, params):
    print "HERE", User.objects.count()
    return User.objects.count()
