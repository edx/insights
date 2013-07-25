''' Decorators for analytics modules.

@view defines a user-visible view
@query defines a machine-readable SOA
@event_handler takes the user tracking event stream
@cron allows for periodic and delayed events
'''


import hashlib
import inspect
import logging
import time



from decorator import decorator

from django.core.cache import cache
from django.conf import settings

from celery.task import PeriodicTask, periodic_task
from util import optional_parameter_call
from util import default_optional_kwargs

import registry
from registry import event_handlers, request_handlers

log=logging.getLogger(__name__)

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

    TODO: human_name: Name without Python name restrictions -- e.g.
    "Daily uploads" instead of "daily_uploads" -- for use in
    human-usable dashboards.
    '''
    def view_factory(f):
        registry.register_handler('view',category, name, description, f, args)
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
        registry.register_handler('query',category, name, description, f, args)
        return f
    return query_factory


class MemoizeNotInCacheError(Exception):
    pass


class MemoizeAttributeError(Exception):
    pass


def use_forcememoize(func):
    """
    Forces memoization for a function func that has been decorated by
    @memoize_query. This means that it will always redo the computation
    and store the results in cache, regardless of whether a cached result
    already exists.
    """
    if hasattr(func, 'force_memoize'):
        return func.force_memoize
    else:
        raise MemoizeAttributeError("Function %s does not have attribute %s" %
        func.__name__, "force_memoize")


def use_fromcache(func):
    """
    Forces retrieval from cache for a function func that has been decorated by
    @memoize_query. This means that it will try to get the result from cache.
    If the result is not available in cache, it will throw an exception instead
    of computing the result.
    """
    if hasattr(func, 'from_cache'):
        return func.from_cache
    else:
        raise MemoizeAttributeError("Function %s does not have attribute %s" %
        func.__name__, "from_cache")


def use_clearcache(func):
    if hasattr(func, 'clear_cache'):
        return func.clear_cache
    else:
        raise MemoizeAttributeError("Function %s does not have attribute %s" %
        func.__name__, "clear_cache")

# classes to ignore when creating a cache key
from pymongo.database import Database
import fs.osfs
from core.util import CacheHelper
import django.core.cache
DEFAULT_IGNORES = (Database, fs.osfs, CacheHelper, django.core.cache)

def memoize_query(cache_time = 60*4, timeout = 60*15, ignores = DEFAULT_IGNORES):
    ''' Call function only if we do not have the results for its execution already
        We ignore parameters of type pymongo.database.Database and fs.osfs.OSFS. These
        will be different per call, but function identically.

        key_override: use this as a cache key instead of computing a key from the
        function signature.
    '''

    # Helper functions
    def isuseful(a):
        if hasattr(a, 'memoize_ignore') and a.memoize_ignore is True:
            return False
        return True


    def make_cache_key(f, args, kwargs):
        """
        Makes a cache key out of the function name and passed arguments

        Assumption: dict gets dumped in same order
        Arguments are serializable. This is okay since
        this is just for SOA queries, but may break
        down if this were to be used as a generic
        memoization framework
        """

        m = hashlib.new("md4")
        s = str({'uniquifier': 'anevt.memoize',
                 'name' : f.__name__,
                 'file' : inspect.getmodule(f).__file__,
                 'args': [a for a in args if isuseful(a)],
                 'kwargs': kwargs})
        m.update(s)
        key = m.hexdigest()
        return key

    def compute_and_cache(f, key, args, kwargs):
        """
        Runs f and stores the results in cache
        """

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


    def get_from_cache_if_possible(f, key):
        """
        Tries to retrieve the result from cache, otherwise returns None
        """
        cached = cache.get(key)
        # If we're already computing it, wait to finish
        # computation
        while cached == 'Processing':
            cached = cache.get(key)
            time.sleep(0.1)
        # At this point, cached should be the result of the
        # cache line, unless we had a failure/timeout, in
        # which case, it is false
        results = cached
        return results

    def factory(f):


        def operation_mode_default(f, *args, **kwargs):
            # Get he result from cache if possible, otherwise recompute
            # and store in cache
            key = make_cache_key(f, args, kwargs)
            results = get_from_cache_if_possible(f, key)
            if results:
                #print "Cache hit %s %s" % (f.__name__, key)
                pass
            else:
                #print "Cache miss %s %s" % (f.__name__, key)
                results = compute_and_cache(f,key, args, kwargs)
            return results

        def operation_mode_forcememoize(*args, **kwargs):
            # Recompute and store in cache, regardless of whether key
            # is in cache.
            key = make_cache_key(f, args, kwargs)
            # print "Forcing memoize %s %s " % (f.__name__, key)
            results = compute_and_cache(f, key, args, kwargs)
            return results

        def operation_mode_fromcache(*args, **kwargs):
            # Retrieve from cache if possible otherwise throw an exception
            # print "Forcing retrieve %s %s " % (f.__name__, key)
            key = make_cache_key(f, args, kwargs)
            results = get_from_cache_if_possible(f, key)
            if not results:
                raise MemoizeNotInCacheError('key %s not found in cache' % key)
            return results

        def operation_mode_clearcache(*args, **kwargs):
            key = make_cache_key(f, args, kwargs)

            return cache.delete(key)

        decfun = decorator(operation_mode_default,f)
        decfun.force_memoize = operation_mode_forcememoize   # activated by use_forcememoize
        decfun.from_cache = operation_mode_fromcache  # activated by use_fromcache
        decfun.clear_cache = operation_mode_clearcache
        return decfun
    return factory

def cron(run_every, force_memoize=False, params={}):
    ''' Run command periodically

    force_memoize: if the function being decorated is also decorated by
    @memoize_query, setting this to True will redo the computation
    regardless of whether the results of the computation already exist in cache

    The task scheduler process (typically celery beat) needs to be started 
    manually by the client module with:
    python manage.py celery worker -B --loglevel=INFO
    Celery beat will automatically add tasks from files named 'tasks.py'    
    '''
    def factory(f):
        @periodic_task(run_every=run_every, name=f.__name__)
        def run(func=None, *args, **kw):
            # This function can be called from two distinct places. It can be
            # called by the task scheduler (due to @periodic_task),
            # in which case func will be None.
            # It can also be called as a result of calling the function we
            # are currently decorating with @cron. In this case func will be
            # the same as f.

            # Was it called from the task scheduler?
            called_as_periodic = True if func is None else False

            if called_as_periodic:
                #print "called as periodic"
                if force_memoize:
                    func = use_forcememoize(f)
                else:
                    func = f
            else:
                #print "called from code"
                func = f

            result = optional_parameter_call(func, default_optional_kwargs, params)

            return result
        return decorator(run, f)
    return factory

def event_property(name=None, description=None):
    ''' This is used to add properties to events. 

    E.g. a module could add the tincan properties such that other
    analytics modules could access event properties generically. 
    '''
    def register(f):
        registry.register_event_property(f, name, description)
        return f
    return register

