import inspect
import json
import os

from django.core.urlresolvers import reverse
from django.dispatch import receiver
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.csrf import csrf_exempt

from fs.osfs import OSFS
from pymongo import MongoClient

from django.conf import settings

from djeventstream.signals import event_received

from decorators import event_handlers, request_handlers


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
    ''' Returns all available views and queries as a JSON
    object. Alternative to the probe hierarchy. 

    '''
    endpoints = []
    for cls in request_handlers:
        for category in request_handlers[cls]:
            for details in request_handlers[cls][category]:
                endpoints.append({'type' : cls, 'category' : category, 'name' : details})
    return HttpResponse(json.dumps(endpoints))

optional_kwargs = {'fs' : get_filesystem, 
                   'db' : get_database}

def optional_parameter_call(function, optional_kwargs, passed_kwargs, arglist = None): 
    ''' UNTESTED/in development

    Calls a function with parameters: 
    passed_kwargs are input parameters the function must take. 
    Format: Dictionary mapping keywords to arguments. 

    optional_kwargs are optional input parameters. 
    Format: Dictionary mapping keywords to functions which generate those parameters. 

    arglist is an optional list of arguments to pass to the function. 
    '''
    if not arglist: 
        arglist = inspect.getargspec(handler).args
    
    args = {}
    for arg in arglist:
        # This order is important for security. We don't want users
        # being able to pass in 'fs' or 'db' and having that take
        # precedence. 
        if arg in optional_kwargs:
            args[arg] = optional_kwargs[arg](function)
        elif arg in passed_kwargs: 
            args[arg] = passed_kwargs[arg]
        else: 
            raise TypeError("Missing argument needed for handler ", arg)
    function(**args)

def handle_request(request, cls, category, name, **kwargs):
    ''' Generic code from handle_view and handle_query '''
    args = dict()
    handler_dict = request_handlers[cls][category][name]
    handler = handler_dict['function']
    if 'args' in handler_dict:
        arglist = handler_dict['arglist']
    else:
        arglist = inspect.getargspec(handler).args

    passed_kwargs = {}
    passed_kwargs.update(request.GET)
    passed_kwargs.update(request.POST)
    passed_kwargs.update({'request' : request})
    for arg in arglist:
        if arg == 'db':
            args[arg] = get_database(handler)
        elif arg == 'fs':
            args[arg] = get_filesystem(handler)
        elif arg == 'params':
            args[arg] = passed_kwargs
        else:
            if arg in kwargs:
                args[arg] = kwargs[arg]
            elif arg in passed_kwargs:
                args[arg] = passed_kwargs[arg][0]
            else:
                

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

@receiver(event_received)
def handle_event(sender, **kwargs):
    msg = kwargs['msg']
    if isinstance(msg,list):
        for i in xrange(0,len(msg)):
            try:
                msg[i] = json.loads(msg[i])
            except:
                pass

    for e in event_handlers:
        event_func = e['function']
        batch = e['batch']
        fs = get_filesystem(event_func)
        database = get_database(event_func)
        if not isinstance(msg,list): ## Message was a single event
            try:
                event_func(fs, database, [msg])
            except:
                handle_event_exception(e['function'])
        elif not batch: ## Message was a list of events, but handler cannot batch events
            for event in msg:
                try:
                    event_func(fs, database, [event])
                except:
                    handle_event_exception(e['function'])
        else: ## Message was a list of events, and handler can batch events
            try:
                event_func(fs, database, msg)
            except:
                handle_event_exception(e['function'])

    return HttpResponse( "Success" )

def handle_event_exception(function):
    log.exception("Handler {0} failed".format(function))

