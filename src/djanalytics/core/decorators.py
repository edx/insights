''' Decorators for analytics modules. 

@view defines a user-visible view
@query defines a machine-readable SOA
@event_handler takes the user tracking event stream
@cron allows for periodic and delayed events
'''


import hashlib
import inspect
import json
import logging
import time
import traceback

from datetime import timedelta
from decorator import decorator

from django.core.cache import cache
from django.conf import settings

from celery.task import PeriodicTask, periodic_task

log=logging.getLogger(__name__)

event_handlers = []

request_handlers = {'view':{}, 'query':{}}

def event_handler(batch=True, per_user=False, per_resource=False,
    single_process=False, source_queue=None):
    ''' Decorator to register an event handler.

    batch=True ==> Normal mode of operation. Cannot break system (unimplemented)
    batch=False ==> Event handled immediately operation. Slow handlers can break system.

    per_user = True ==> Can be sharded on a per-user basis (default: False)
    per_resource = True ==> Can be sharded on a per-resource basis (default: False)

    single_process = True ==> Cannot be distributed across process/machines. Queued must be true.

    source_queue ==> Not implemented. For a pre-filter (e.g. video)
    '''

    if single_process or source_queue or not batch:
        raise NotImplementedError("Framework isn't done. Sorry. batch=True, source_queue=None, single_proces=False")
    def event_handler_factory(func):
        event_handlers.append({'function' : func, 'batch' : batch})
        return func
    return event_handler_factory

import views # TODO: Clean up imports/where functions live

funcskips = views.default_optional_kwargs.keys()+['params'] # params are additional GET/POST parameters
funcspecs = [ ([], 'global') ] 

def register_handler(cls, category, name, description, f, args):
    ''' Helper function for @view and @query decorators. 
    '''
    log.debug("Register {0} {1} {2} {3}".format(cls, category, name, f))
    if args == None:
        args = inspect.getargspec(f).args
    if cls not in ['view', 'query']:
        raise ValueError("We can only register views and queries")
    if not name:
        name = str(f.func_name)
    if not description:
        description = str(f.func_doc)
    if not category:
        url_argspec = [a for a in inspect.getargspec(f).args if a not in funcskips]
        found_in_funcspec = False
        for (params, cat) in funcspecs:
            if url_argspec == params:
                category = cat
                found_in_funcspec = True
        if not found_in_funcspec:
            category=""
            for i in xrange(0,len(url_argspec)):
                spec = url_argspec[i]
                category += "{0}".format(spec)
                if i!= len(url_argspec) -1:
                    category+="+"
            funcspecs.append((url_argspec, category))
            log.debug(funcspecs)
    if not category:
        pass
        #raise ValueError('Function arguments do not match recognized type. Explicitly set category in decorator.')
    if cls not in request_handlers:
        request_handlers[cls] = {}
    if category not in request_handlers[cls]:
        request_handlers[cls][category]={}
    if name in request_handlers[cls][category]:
        # We used to have this be an error.
        # We changed to a warning for the way we handle dummy values.
        log.warn("{0} already in {1}".format(name, category))  # raise KeyError(name+" already in "+category)
    request_handlers[cls][category][name] = {'function': f, 'name': name, 'doc': description}

def view(category = None, name = None, description = None, args = None):
    ''' This decorator is appended to a view in an analytics module. A
    view will return HTML which will be shown to the user. 

    category: Optional specification for type (global, per-user,
      etc.). If not given, this will be extrapolated from the
      argspec. This should typically be omitted. 

    name: Optional specification for name shown to the user. This will
      default to function name. In most cases, this is recommended.

    description: Optional description. If not given, this will default
      to the docstring.

    args: Optional argspec for the function. This is generally better
      omitted. 
    '''
    def view_factory(f):
        register_handler('view',category, name, description, f, args)
        return f
    return view_factory

def query(category = None, name = None, description = None, args = None):
    ''' This decorator is appended to a query in an analytics
    module. A module will return output that can be used
    programmatically (typically JSON). 

    category: Optional specification for type (global, per-user,
      etc.). If not given, this will be extrapolated from the
      argspec. This should typically be omitted. 

    name: Optional specification for name exposed via SOA. This will
      default to function name. In most cases, this is recommended. 

    description: Optional description exposed via the SOA
      discovery. If not given, this will default to the docstring. 

    args: Optional argspec for the function. This is generally better
      omitted. 
    '''
    def query_factory(f):
        register_handler('query',category, name, description, f, args)
        return f
    return query_factory


def memoize_query(cache_time = 60*4, timeout = 60*15, ignores = ["<class 'pymongo.database.Database'>", "<class 'fs.osfs.OSFS'>"]):
    ''' Call function only if we do not have the results for its execution already
        We ignore parameters of type pymongo.database.Database and fs.osfs.OSFS. These
        will be different per call, but function identically. 
    '''
    def isuseful(a, ignores):
        if str(type(a)) in ignores:
            return False
        return True

    def view_factory(f):
        def wrap_function(f, *args, **kwargs):
            # Assumption: dict gets dumped in same order
            # Arguments are serializable. This is okay since
            # this is just for SOA queries, but may break
            # down if this were to be used as a generic
            # memoization framework
            m = hashlib.new("md4")
            s = str({'uniquifier': 'anevt.memoize',
                     'name' : f.__name__,
                     'module' : f.__module__,
                     'args': [a for a in args if isuseful(a, ignores)],
                     'kwargs': kwargs})
            m.update(s)
            key = m.hexdigest()
            # Check if we've cached the computation, or are in the
            # process of computing it
            cached = cache.get(key)
            if cached:
                #print "Cache hit", key
                # If we're already computing it, wait to finish
                # computation
                while cached == 'Processing':
                    cached = cache.get(key)
                    time.sleep(0.1)
                    # At this point, cached should be the result of the
                # cache line, unless we had a failure/timeout, in
                # which case, it is false
                results = cached

            if not cached:
                #print "Cache miss", key
                # HACK: There's a slight race condition here, where we
                # might recompute twice.
                cache.set(key, 'Processing', timeout)
                function_argspec = inspect.getargspec(f)
                if function_argspec.varargs or function_argspec.args:
                    if function_argspec.keywords:
                        results = f(*args, **kwargs)
                    else:
                        results = f(*args)
                else:
                    results = f()
                cache.set(key, results, cache_time)

            return results
        return decorator(wrap_function,f)
    return view_factory

def cron(period, params=None):
    ''' Run command periodically
    
    Unknown whether or how well this works. 
    '''
    def factory(f):
        @periodic_task(run_every=period, name=f.__name__)
        def run():
            import djanalytics.core.views
            db = core.views.get_database(f)
            fs = core.views.get_filesystem(f)
            f(fs, db, params)
        return decorator(run,f)
    return factory

event_property_registry = {}

def register_event_property(f, name, description):
    ''' helper for event_property decorator '''
    if not name:
        name = str(f.func_name)
    if not description:
        description = str(f.func_doc)
    event_property_registry[name] = {'function': f, 'name': name, 'doc': description}

def event_property(name=None, description=None):
    def register(f):
        register_event_property(f, name, description)
        return f
    return register

class StreamingEvent:
    ''' Event object. Behaves like the normal JSON event dictionary,
    but allows modules to add additional properties. JSON properties
    are gotten with [] (which should be minimally used), while derived
    properties with . For example, a tincan module could add: 

    evt.agent
    evt.verb
    evt.object

    Using these would allow modules to continue working even with
    schema changes (or using this framework with LMSes with different
    event structures).

    It is also immutable. 
    '''
    def __init__(self, event):
        self.event = event

    def __contains__(self, key):
        return key in self.event

    def __getitem__(self, key):
        return self.event[key]

    def __getattr__(self, key):
        if key in event_property_registry:
            return event_property_registry[key]['function'](self)
        else: 
            raise AttributeError("StreamingEvent has no attribute "+key)

    def __str__(self):
        return "Event:"+self.event.__str__()

    def __repr__(self):
        return "Event:"+self.event.__repr__()

    def keys(self):
        return self.event.keys()
