# The django cache is used by core.memoize_query to store results temporarily.
# Because periodic tasks are run from a separate process, and
# because periodic tasks could also be memoized, the
# django cache backend has to be visible across processes.
# Most django.cache.core.backends would work except for LocMemCache

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        # files in /tmp older than TMPTIME specified in /etc/default/rcS
        # are erased automatically on reboot.
        # Make sure the specified directory in LOCATION is writeable by apache
        'LOCATION': '/tmp/django_cache/',
        'TIMEOUT': 60*60, #one hour
        'OPTIONS' : {
            'MAX_ENTRIES' : 100
        }
    }
}