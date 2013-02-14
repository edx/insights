import atexit
import logging
import os
import sys
import imp
import tempfile

from django.conf import settings
from django.utils.importlib import import_module

import cronjobs

log = logging.getLogger('cron')

LOCK = getattr(settings, 'CRONJOB_LOCK_PREFIX', 'lock')

def run_single_job(script, *args):
    for app in settings.INSTALLED_APPS:
        try:
            app_path = import_module(app).__path__
        except AttributeError:
            continue

        try:
            imp.find_module('cron', app_path)
        except ImportError as e:
            continue

        import_module('%s.cron' % app)

    registered = cronjobs.registered

    if script not in registered:
        log.error("Cron called with unrecognized command: %s %s" %
                  (script, args))
        print 'Unrecognized name: %s' % script
        sys.exit(1)

    # Acquire lock if needed.
    if script in cronjobs.registered_lock:
        filename = os.path.join(tempfile.gettempdir(),
                                'django_cron.%s.%s' % (LOCK, script))
        try:
            fd = os.open(filename, os.O_CREAT|os.O_EXCL)

            def register():
                os.close(fd)
                os.remove(filename)

            atexit.register(register)
        except OSError:
            msg = ("Script run multiple times. If this isn't true, delete "
                   "`%s`." % filename)
            log.error(msg)
            sys.stderr.write(msg + "\n")
            sys.exit(1)

    log.info("Beginning job: %s %s" % (script, args))
    registered[script](*args)
    log.info("Ending job: %s %s" % (script, args))
