# Create your views here.

from django.http import HttpResponse
import json
from an_evt.models import StudentBookAccesses
from django.utils.datastructures import MultiValueDictKeyError

event_handlers = []
view_handlers = {}
query_handlers = {}

def handle_list(request):
    pass

def handle_query(request):
    pass

def handle_event(request):
    try: # Not sure why this is necessary, but on some systems it is 'msg', and on others, 'message'
        response = json.loads(request.GET['message'])
    except MultiValueDictKeyError: 
        response = json.loads(request.GET['msg'])

    for e in event_handlers:
        e(response)

    return HttpResponse( "Success" )

def handle_view(request, category, name, param1=None, param2=None):
    ''' Handles generic view. 
        Category is where this should be place (per student, per problem, etc.)
        Name is specific 
    '''
    if category == 'user':
        username = param1
        return HttpResponse( view_handlers[category][name](username, request.GET))

def event_handler(queued=True, per_user=False, single_process=False, per_resource=False, source_queue=None):
    ''' Decorator to register an event handler. 

    queued=True ==> Normal mode of operation. Cannot break system (unimplemented)
    queued=False ==> Event handled immediately operation. Slow handlers can break system. 

    per_user = True ==> Can be sharded on a per-user basis (default: False)
    per_resource = True ==> Can be sharded on a per-resource basis (default: False)

    single_process = True ==> Cannot be distributed across process/machines. Queued must be true. 
    
    source_queue ==> Not implemented. For a pre-filter (e.g. video)
    '''
    def event_handler_factory(func):
        event_handlers.append(func)
        return func
    return event_handler_factory

def view(category, name):
    def view_factory(a):
        if category not in view_handlers:
            view_handlers[category]={}
        if name in view_handlers[category]:
            raise KeyError(name+" already in "+category)
        view_handlers[category][name] = a

        return a
    return view_factory

def query(category, name):
    def query_factory(a):
        return a
    return query_factory

''' Sample views/events. Should be moved to a new file. 
'''

@view('user', 'page_count')
def book_page_count_view(user, params):
    #user = request.GET['uid']

    return "The user " + user + " saw "+str(book_page_count_query(user, params))+" pages!"

@query('user', 'page_count')
def book_page_count_query(user, params):
    sba = StudentBookAccesses.objects.filter(username = user)
    if len(sba):
        pages = sba[0].count
    else: 
        pages = 0
    return pages

@event_handler()
def book_page_count_event(response):
    sba = StudentBookAccesses.objects.filter(username = response["username"])
    if len(sba) == 0:
        sba = StudentBookAccesses()
        sba.username = response["username"]
        sba.count = 0
    else:
        sba=sba[0]
    sba.count = sba.count + 1
    sba.save()
    pass
