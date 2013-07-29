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

from celery.task import periodic_task
from util import optional_parameter_call

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
    """ Raised when using use_fromcache and the requested cache key is not in
    the cache
    """
    pass


class MemoizeAttributeError(Exception):
    """ Raised when requesting to use one of a function's following attributes:
    force_memoize, from_cache, clear_cache, but the function does not have the
    requested attribute because it was not decorated by @memoize_query
    """
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

def memoize_query(cache_time = 60*4, timeout = 60*15, ignores = ()):
    ''' Call function only if we do not have the results for its execution already

        ignores: a list of classes to ignore when creating a cache key. Arguments
        having a memoize_ignore attribute set to True are automatically ignored.
    '''

    # Helper functions
    def isuseful(a):
        if hasattr(a, 'memoize_ignore') and a.memoize_ignore is True and not isinstance(a, ignores):
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

        HACK: There's slight race condition here, where we might recompute twice
        """
        if cache.get(key) is None:
            # While processing the request set the cache value to a unique
            # string that cannot be mistaken for an actual result. Do this
            # only if there was not cached result already -- this will allow
            # callers to access the old cached value while we compute the new.
            cache.set(key, 'Processing-14c44a51-31a6-4ba0-aed5-a52164ce4613', timeout)

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
        while cached == 'Processing-14c44a51-31a6-4ba0-aed5-a52164ce4613':
            cached = cache.get(key)
            time.sleep(0.1)
        # At this point, cached should be the result of the
        # cache line, unless we had a failure/timeout, in
        # which case, it is false
        results = cached
        return results

    def factory(f):

        def operationmode_default(f, *args, **kwargs):
            """ Get he result from cache if possible, otherwise recompute
            and store in cache
            """
            key = make_cache_key(f, args, kwargs)
            results = get_from_cache_if_possible(f, key)
            if results:
                # we got the results from cache, do not recompute
                pass
            else:
                results = compute_and_cache(f,key, args, kwargs)
            return results

        def operationmode_forcememoize(*args, **kwargs):
            """ Recompute and store in cache, regardless of whether key
            is in cache.
            """
            key = make_cache_key(f, args, kwargs)
            results = compute_and_cache(f, key, args, kwargs)
            return results

        def operationmode_fromcache(*args, **kwargs):
            """ Retrieve from cache if possible otherwise throw an exception
            """
            key = make_cache_key(f, args, kwargs)
            results = get_from_cache_if_possible(f, key)
            if not results:
                raise MemoizeNotInCacheError('key %s not found in cache' % key)
            return results

        def operation_mode_clearcache(*args, **kwargs):
            key = make_cache_key(f, args, kwargs)

            return cache.delete(key)

        decfun = decorator(operationmode_default,f)
        decfun.force_memoize = operationmode_forcememoize   # activated by use_forcememoize
        decfun.from_cache = operationmode_fromcache  # activated by use_fromcache
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
            """ Executes the function decorated by @cron

                This function can be called from two distinct places. It can be
                called by the task scheduler (due to @periodic_task),
                in which case func will be None.

                It can also be called as a result of calling the function we
                are currently decorating with @cron. In this case func will be
                the same as f.
            """

            # Was it called from the task scheduler?
            called_as_periodic = True if func is None else False

            if called_as_periodic:
                if force_memoize:
                    func = use_forcememoize(f)
                else:
                    func = f
            else:
                func = f

            result = optional_parameter_call(func, params)

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

