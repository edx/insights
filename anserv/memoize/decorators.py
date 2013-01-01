from django.core.cache import cache
import time

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
