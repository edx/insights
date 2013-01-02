import json
import os

from django.http import HttpResponse
from django.utils.datastructures import MultiValueDictKeyError

from django.conf import settings

from fs.osfs import OSFS

from modules.decorators import event_handlers, request_handlers



### HACK ###
# This is the way in which we activate modules, pending a proper
# loader
import modules.page_count.book_count
import modules.user_stats.user_stats
### END HACK ###



from pymongo import MongoClient
connection = MongoClient()
#db = connection['analytic_store']

def get_database(f):
    ''' Given a function in a module, return the Mongo DB associated
    with that function. 
    '''
    return connection[str(f.__module__).replace(".","_")]

def get_filesystem(f):
    ''' Given a function in a module, return the Pyfilesystem for that
    function. Right now, this is on disk, but it has to move to
    Mongo gridfs or S3 or similar (both of which are supported by 
    pyfs).
    '''
    directory = settings.MODULE_RESOURCE_STATIC + '/' + str(f.__module__).replace(".","_")
    if not os.path.exists(directory):
        os.mkdir(directory)
    
    return OSFS(directory)

def handle_probe(request, cls=None, category=None, details = None):
    ''' Handles probes for what types of modules are available, and
    what they do. Shown as, effectively, a big directory tree to the
    caller.
    '''
    if cls == None:
        l = ['view','query']
    elif category == None:
        l = request_handlers[cls].keys()
    elif details == None:
        l = request_handlers[cls][category].keys()
    else: 
        l = [request_handlers[cls][category][details]['doc']]
    return HttpResponse("\n".join(l), mimetype='text/text')

def handle_view(request, category, name, param1=None, param2=None):
    ''' Handles generic view. 
        Category is where this should be place (per student, per problem, etc.)
        Name is specific 
    '''
    handler = request_handlers['view'][category][name]['function']
    database = get_database(handler)
    fs = get_filesystem(handler)
    if category == 'user':
        username = param1
        return HttpResponse( handler(fs, database, username, request.GET))

    if category == 'global': 
        return HttpResponse( handler(fs, database, request.GET))


def handle_query(request, category, name, param1=None, param2=None):
    ''' Handles programmatic queries to retrieve analytics data. 

    Cut-and-paste code from an old version of handle_view. Should be
    made generic to both. 
    '''
    if category == 'user':
        username = param1
        handler = request_handlers['query'][category][name]['function']
        database = get_database(handler)
        fs = get_filesystem(handler)
        return HttpResponse( handler(fs, database, username, request.GET))

def handle_event(request):
    try: # Not sure why this is necessary, but on some systems it is 'msg', and on others, 'message'
        response = json.loads(request.GET['message'])
    except MultiValueDictKeyError: 
        response = json.loads(request.GET['msg'])

    for e in event_handlers:
        fs = get_filesystem(e)
        database = get_database(e)
        e(fs, database, response)

    return HttpResponse( "Success" )

