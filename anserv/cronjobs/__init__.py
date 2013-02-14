registered = {}
registered_lock = {}
parameters = {}
from decorator import decorator

def register(f=None, lock=True, params={}):
    """Decorator to add the function to the cronjob library.

        @cronjobs.register
        def my_task():
            print('I can be run once/machine at a time.')

        @cronjobs.register(lock=False)
        def my_task():
            print('I am concurrent friendly!')

    """

    def cron_decorator(f, lock=lock):
        registered[f.__name__] = f
        parameters[f.__name__] = params
        if lock:
            registered_lock[f.__name__] = f
        return f

    if callable(f):
        return decorator(cron_decorator(f, lock),f)
    return cron_decorator
