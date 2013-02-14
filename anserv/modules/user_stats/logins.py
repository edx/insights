from modules.decorators import view, query, event_handler, memoize_query
import datetime
from django.contrib.auth.models import User


@query()
def query_logins():
    last_minute = User.objects.all().filter(last_login__gte = User.objects.order_by('-last_login')[0].last_login - datetime.timedelta(minutes=1) ).count()
    last_hour = User.objects.all().filter(last_login__gte = User.objects.order_by('-last_login')[0].last_login - datetime.timedelta(hours=1) ).count()
    last_day = User.objects.all().filter(last_login__gte = User.objects.order_by('-last_login')[0].last_login - datetime.timedelta(days=1) ).count()
    last_week = User.objects.all().filter(last_login__gte = User.objects.order_by('-last_login')[0].last_login - datetime.timedelta(weeks=1) ).count()
    return (last_minute, last_hour, last_day, last_week)
