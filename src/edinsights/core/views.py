import inspect
import json
import os

from django.core.urlresolvers import reverse
from django.dispatch import receiver
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.csrf import csrf_exempt

from django.conf import settings

from djeventstream.signals import event_received

from registry import event_handlers, request_handlers
from util import default_optional_kwargs

import auth
import util
from util import optional_parameter_call

import logging

log=logging.getLogger(__name__)

@auth.auth
def index(request):
    return HttpResponseRedirect("static/index.html")

@auth.auth
def event_properties(request):
    ''' Adds a view to advertise defined event properties '''
    from registry import event_property_registry
    items = []
    for key in event_property_registry.keys():
        items.append("<di>{name}</di><dd>{doc}</dd>".format(**event_property_registry[key]))
    return HttpResponse("<dl>"+"\n".join(items)+"</dl>")

@auth.auth
def schema(request):
    ''' Returns all available views and queries as a JSON
    object. 
    '''
    from registry import schema_helper
    endpoints = schema_helper()
    if request.GET.get("f", "") == "html":
        return HttpResponse("\n".join(sorted(["<dt><p><b>{class}/{name}</b> <i>{category}</i></dt><dd>{doc}</dd>".format(**rh) for rh in endpoints])))
    return HttpResponse(json.dumps(endpoints))

view_object=None    
@auth.auth
def handle_view(request, name, **kwargs):
    ''' Handles generic view. 
        Category is where this should be place (per student, per problem, etc.)
        Name is specific 
    '''
    global view_object
    if view_object is None: 
        from util import get_view
        view_object = get_view(None)
    if name[0] == '_':
        raise SuspiciousOperation(name+' called')
    kwargs.update(request.POST.items())
    kwargs.update(request.GET.items())
    results = view_object.__getattr__(name)(**kwargs)
    return HttpResponse(results)

query_object = None
@auth.auth
def handle_query(request, name, **kwargs):
    ''' Handles generic view. 
        Category is where this should be place (per student, per problem, etc.)
        Name is specific 
    '''
    global query_object
    if query_object is None: 
        from util import get_query
        query_object = get_query(None)
    if name[0] == '_':
        raise SuspiciousOperation(name+' called')
    kwargs.update(request.POST.items())
    kwargs.update(request.GET.items())
    results = query_object.__getattr__(name)(**kwargs)
    if isinstance(results, basestring):
        return HttpResponse(results)
    else:
        return HttpResponse(json.dumps(results))

@receiver(event_received)
def handle_event(sender, **kwargs):
    ''' Receives either an event or a list of events, as sent by
    djeventstream (either from a Python logging HTTPHandler or
    SNSHandler. 

    Forwards it along to the event handlers defined in the modules. 

    This is not a view, but it is the moral equivalent. 
    '''
    # Handle strings, lists, and dictionaries
    # TODO handle errors if not valid json
    msg = kwargs['msg']
    if isinstance(msg,str) or isinstance(msg,unicode):
        msg = json.loads(msg)

    # If we get a batch of events, we need to load them. 
    if isinstance(msg,list):
        for i in xrange(0,len(msg)):
            try:
                msg[i] = json.loads(msg[i])
            except:
                pass

    # Single event should still be passed as a list for API 
    # compatibility between patched and unbatched. 
    if not isinstance(msg, list):
        msg = [msg]
    
    from registry import StreamingEvent
    msg = map(StreamingEvent, msg)

    for e in event_handlers:
        event_func = e['function']
        batch = e['batch']
        if not batch: ## Message was a list of events, but handler cannot batch events
            for event in msg:
                try:
                    optional_parameter_call(event_func, default_optional_kwargs, {'events':[event]})
                except:
                    handle_event_exception(e['function'])
        else: ## Message was a list of events, and handler can batch events
            try:
                optional_parameter_call(event_func, default_optional_kwargs, {'events':msg})
            except:
                handle_event_exception(e['function'])

    return HttpResponse( "Success" )

def handle_event_exception(function):
    log.exception("Handler {0} failed".format(function))

