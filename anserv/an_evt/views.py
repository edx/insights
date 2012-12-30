# Create your views here.

from django.http import HttpResponse
import json
from an_evt.models import StudentBookAccesses
from django.utils.datastructures import MultiValueDictKeyError
from modules.decorators import event_handlers, request_handlers

import inspect

### HACK ###
import modules.page_count.book_count
import modules.user_stats.user_stats
### END HACK ###

from pymongo import MongoClient
connection = MongoClient()
#db = connection['analytic_store']

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
        handler = request_handlers['query'][category][name]['function']
        collection = connection[str(handler.__module__).replace(".","_")]
        print "Module: "+str(handler.__module__)
        return HttpResponse( handler(collection, username, request.GET))

def handle_event(request):
    try: # Not sure why this is necessary, but on some systems it is 'msg', and on others, 'message'
        response = json.loads(request.GET['message'])
    except MultiValueDictKeyError: 
        response = json.loads(request.GET['msg'])

    for e in event_handlers:
        collection = connection[str(e.__module__).replace(".","_")]
        e(collection, response)

    return HttpResponse( "Success" )

def handle_view(request, category, name, param1=None, param2=None):
    ''' Handles generic view. 
        Category is where this should be place (per student, per problem, etc.)
        Name is specific 
    '''
    handler = request_handlers['view'][category][name]['function']
    collection = connection[str(handler.__module__).replace(".","_")]
    if category == 'user':
        username = param1
        return HttpResponse( handler(collection, username, request.GET))

    if category == 'global': 
        return HttpResponse( handler(collection, request.GET))
