# Create your views here.

from django.http import HttpResponse
import json
from an_evt.models import StudentBookAccesses
from django.utils.datastructures import MultiValueDictKeyError

events = []

def handle_event(request):
    try: # Not sure why this is necessary, but on some systems it is 'msg', and on others, 'message'
        response = json.loads(request.GET['message'])
    except MultiValueDictKeyError: 
        response = json.loads(request.GET['msg'])

    for e in events:
        e(response)

    return HttpResponse( "Success" )

def user_render(request):
    user = request.GET['uid']
    print user

    sba = StudentBookAccesses.objects.filter(username = user)
    if len(sba):
        pages = sba[0].count
    else: 
        pages = 0


    return HttpResponse( "The user " + user + " saw "+str(pages)+" pages!" )

def event_handler(func, queued=True, per_user=False, single_process=False, per_resource=False, source_queue=None):
    ''' Decorator to register an event handler. 

    queued=True ==> Normal mode of operation. Cannot break system (unimplemented)
    queued=False ==> Event handled immediately operation. Slow handlers can break system. 

    per_user = True ==> Can be sharded on a per-user basis (default: False)
    per_resource = True ==> Can be sharded on a per-resource basis (default: False)

    single_process = True ==> Cannot be distributed across process/machines. Queued must be true. 
    
    source_queue ==> Not implemented. For a pre-filter (e.g. video)
    '''
    events.append(func)
    return func

def view(a):
    return a

@view
def book_page_count_view(request):
    pass

@event_handler
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
