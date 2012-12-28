# Create your views here.

from django.http import HttpResponse
import json
from an_evt.models import StudentBookAccesses
from django.utils.datastructures import MultiValueDictKeyError
from modules.decorators import event_handlers, request_handlers
import modules.page_count.book_count

from pymongo import MongoClient
connection = MongoClient()
db = connection['analytic_store']

def handle_list(request, cls=None, category=None):
    if cls == None:
        l = ['view','query']
    elif category == None:
        l = request_handlers[cls].keys()
    else:
        l = request_handlers[cls][category].keys()
    return HttpResponse("\n".join(l), mimetype='text/text')

def handle_query(request, category, name, param1=None, param2=None):
    if category == 'user':
        username = param1
        handler = request_handlers['query'][category][name]
        collection = db[str(handler.__module__)]
        print "Module: "+str(handler.__module__)
        return HttpResponse( handler(collection, username, request.GET))

def handle_event(request):
    try: # Not sure why this is necessary, but on some systems it is 'msg', and on others, 'message'
        response = json.loads(request.GET['message'])
    except MultiValueDictKeyError: 
        response = json.loads(request.GET['msg'])

    for e in event_handlers:
        collection = db[str(e.__module__)]
        e(collection, response)

    return HttpResponse( "Success" )

def handle_view(request, category, name, param1=None, param2=None):
    ''' Handles generic view. 
        Category is where this should be place (per student, per problem, etc.)
        Name is specific 
    '''
    if category == 'user':
        username = param1
        handler = request_handlers['view'][category][name]
        collection = db[str(handler.__module__)]
        print "Module: "+str(handler.__module__)
        return HttpResponse( handler(collection, username, request.GET))


''' Sample views/events. Should be moved to a new file. 
'''

# @view('user', 'page_count')
# def book_page_count_view(user, params):
#     #user = request.GET['uid']

#     return "The user " + user + " saw "+str(book_page_count_query(user, params))+" pages!"

# @query('user', 'page_count')
# def book_page_count_query(user, params):
#     sba = StudentBookAccesses.objects.filter(username = user)
#     if len(sba):
#         pages = sba[0].count
#     else: 
#         pages = 0
#     return pages

# @event_handler()
# def book_page_count_event(response):
#     sba = StudentBookAccesses.objects.filter(username = response["username"])
#     if len(sba) == 0:
#         sba = StudentBookAccesses()
#         sba.username = response["username"]
#         sba.count = 0
#     else:
#         sba=sba[0]
#     sba.count = sba.count + 1
#     sba.save()
#     pass
