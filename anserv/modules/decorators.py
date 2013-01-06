import inspect
import decorator
from django_cron.base import register, Job
from django.core.cache import cache
import time


import traceback

event_handlers = []

request_handlers = {'view':{}, 'query':{}}

def event_handler(queued=True, per_user=False, per_resource=False, single_process=False, source_queue=None):
    ''' Decorator to register an event handler. 

    queued=True ==> Normal mode of operation. Cannot break system (unimplemented)
    queued=False ==> Event handled immediately operation. Slow handlers can break system. 

    per_user = True ==> Can be sharded on a per-user basis (default: False)
    per_resource = True ==> Can be sharded on a per-resource basis (default: False)

    single_process = True ==> Cannot be distributed across process/machines. Queued must be true. 
    
    source_queue ==> Not implemented. For a pre-filter (e.g. video)
    '''

    if single_process or source_queue or queued:
        raise NotImplementedError("Framework isn't done. Sorry. queued=False, source_queue=None, single_proces=False")
    def event_handler_factory(func):
        event_handlers.append(func)
        return func
    return event_handler_factory

funcspecs = [ (['fs','db','params'], 'global'), 
              (['fs','db','user','params'], 'user') ]

def register_handler(cls, category, name, description, f, args):
    print "Register", cls, category, name, f
    if args == None:
        args = inspect.getargspec(f).args
    print args
#    traceback.print_stack()
    if cls not in ['view', 'query']:
        raise ValueError("We can only register views and queries")
    if not name: 
        name = str(f.func_name)
    if not description: 
        description = str(f.func_doc)
    if not category:
        for (params, cat) in funcspecs:
            if inspect.getargspec(f).args == params:
                category = cat
    if not category: 
        raise ValueError('Function arguments do not match recognized type. Explicitly set category in decorator.')
    if category not in request_handlers[cls]:
        request_handlers[cls][category]={}
    if name in request_handlers[cls][category]:
        # We used to have this be an error. 
        # We changed to a warning for the way we handle dummy values. 
        print "WARNING WARNING WARNING", name, "already in", category  # raise KeyError(name+" already in "+category)
    request_handlers[cls][category][name] = {'function': f, 'name': name, 'doc': description}

def view(category = None, name = None, description = None, args = None):
    def view_factory(f):
        register_handler('view',category, name, description, f, args)
        return f
    return view_factory

def query(category = None, name = None, description = None, args = None):
    ''' 
    ''' 
    def query_factory(f):
        register_handler('query',category, name, description, f, args)
        return f
    return query_factory

def cron(period, params=None):
    ''' Run command periodically
    Command takes database and 
    
    '''
    def factory(f):
        class CronJob(Job):
            run_every = period
            id = f.__module__+'/'+f.__name__
            def job(self):
                import an_evt.views
                db = an_evt.views.get_database(f)
                f(db, params)
        register(CronJob)
        return f
    return factory


def memoize_query(cache_time = 60*4, timeout = 60*15):
    ''' Call function only if we do not have the results for it's execution already
    '''
    
    def view_factory(f):
        def wrap_function(*args, **kwargs):
            # Assumption: dict gets dumped in same order
            # Arguments are serializable. This is okay since
            # this is just for SOA queries, but may break 
            # down if this were to be used as a generic 
            # memoization framework
            key = str({'uniquifier': 'anevt.memoize', 
                       'name' : f.__name__, 
                       'module' : f.__module__, 
                       'args': args, 
                       'kwargs': kwargs})
            # Check if we've cached the computation, or are in the
            # process of computing it
            cached = cache.get(key)
            if cached: 
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
                # HACK: There's a slight race condition here, where we
                # might recompute twice.
                cache.set(key, 'Processing', timeout)
                results = f(*args, **kwargs)
                cache.set(key, results, cache_time)               

            return results
        return wrap_function
    return view_factory

if False: 
    # Test case. Should be made into a proper test case. 
    @memoize_query(1)
    def test_function(x):
        print "Boo", x, ">",2*x
        return 2*x

    print test_function(2)
    print test_function(4)
    print test_function(2)
    print test_function(4)
    time.sleep(2)
    print test_function(2)
    print test_function(4)
    print test_function(2)
    print test_function(4)
