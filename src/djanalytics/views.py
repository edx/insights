import inspect
import json
import os

from django.http import HttpResponse, HttpResponseRedirect
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse

from django.conf import settings

from fs.osfs import OSFS

from decorators import event_handlers, request_handlers

from pymongo import MongoClient
connection = MongoClient()

import logging

log=logging.getLogger(__name__)

def import_view_modules():
    top_level_modules = settings.INSTALLED_ANALYTICS_MODULES
    module_names = []
    for module in top_level_modules:
        mod = __import__(module)
        submodules = []
        try: 
            submodules = mod.modules_to_import # I'd like to deprecate this syntax
        except AttributeError: 
            pass
        for sub_module in submodules:
            submod_name = "{0}.{1}".format(module,sub_module)
            module_names.append(submod_name)
    modules = map(__import__, module_names)
    return modules

modules = import_view_modules()

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
    directory = settings.PROTECTED_DATA_ROOT
    #+ '/' + str(f.__module__).replace(".","_")
    if not os.path.exists(directory):
        os.mkdir(directory)
    
    return OSFS(directory)

def handle_probe(request, cls=None, category=None, details = None):
    ''' Handles probes for what types of modules are available, and
    what they do. Shown as, effectively, a big directory tree to the
    caller.
    '''
    error_message = "{0} not found in {1}."
    if cls == None:
        l = ['view','query']
    elif category == None:
        if cls in request_handlers:
            l = request_handlers[cls].keys()
        else:
            l = [error_message.format(cls,request_handlers)]
    elif details == None:
        if cls in request_handlers and category in request_handlers[cls]:
            l = request_handlers[cls][category].keys()
        else:
            l = [error_message.format(category,request_handlers)]
    else:
        if cls in request_handlers and category in request_handlers[cls] and details in request_handlers[cls][category]:
            l = [request_handlers[cls][category][details]['doc']]
        else:
            l = [error_message.format(details,request_handlers)]
    return HttpResponse("\n".join(l), mimetype='text/text')

def list_all_endpoints(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('django.contrib.auth.views.login'))
    endpoints = []
    for cls in request_handlers:
        for category in request_handlers[cls]:
            for details in request_handlers[cls][category]:
                endpoints.append({'type' : cls, 'category' : category, 'name' : details})
    return HttpResponse(json.dumps(endpoints))

def handle_request(request, cls, category, name, **kwargs):
    ''' Generic code from handle_view and handle_query '''
    args = dict()
    handler_dict = request_handlers[cls][category][name]
    handler = handler_dict['function']
    if 'args' in handler_dict:
        arglist = handler_dict['arglist']
    else:
        arglist = inspect.getargspec(handler).args

    params = {}
    params.update(request.GET)
    params.update(request.POST)
    params.update({'request' : request})
    for arg in arglist:
        if arg == 'db':
            args[arg] = get_database(handler)
        elif arg == 'fs':
            args[arg] = get_filesystem(handler)
        elif arg == 'params':
            args[arg] = params
        else:
            if arg in kwargs:
                args[arg] = kwargs[arg]
            elif arg in params:
                args[arg] = params[arg][0]
            else:
                raise TypeError("Missing argument needed for handler ", arg)

    return handler(**args)

def handle_view(request, category, name, **kwargs):
    ''' Handles generic view. 
        Category is where this should be place (per student, per problem, etc.)
        Name is specific 
    '''
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('django.contrib.auth.views.login'))

    return HttpResponse(handle_request(request, 'view', category, name, **kwargs))

def handle_query(request, category, name, **kwargs):
    ''' Handles generic view. 
        Category is where this should be place (per student, per problem, etc.)
        Name is specific 
    '''
    request_data = handle_request(request, 'query', category, name, **kwargs)
    try:
        request_data = json.dumps(request_data)
    except:
        pass

    try:
        return HttpResponse(request_data)
    except:
        return request_data

@csrf_exempt
def handle_event(request):
    if request.GET:
        try: # Not sure why this is necessary, but on some systems it is 'msg', and on others, 'message'
            response = json.loads(request.GET['message'])
        except MultiValueDictKeyError:
            response = json.loads(request.GET['msg'])
    else:
        try:
            response = json.loads(request.POST['message'])
        except:
            response = json.loads(request.POST['msg'])

    if isinstance(response,list):
        for i in xrange(0,len(response)):
            try:
                response[i] = json.loads(response[i])
            except:
                pass

    for e in event_handlers:
        event_func = e['function']
        batch = e['batch']
        fs = get_filesystem(event_func)
        database = get_database(event_func)
        if not isinstance(response,list):
            try:
                event_func(fs, database, [response])
            except:
                handle_event_exception(e['function'])
        elif not batch:
            for event in response:
                try:
                    event_func(fs, database, [event])
                except:
                    handle_event_exception(e['function'])
        else:
            try:
                event_func(fs, database, response)
            except:
                handle_event_exception(e['function'])

    return HttpResponse( "Success" )

def handle_event_exception(function):
    log.exception("Handler {0} failed".format(function))

