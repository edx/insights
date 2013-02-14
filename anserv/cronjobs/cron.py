import logging
import imp

from django.conf import settings
from django.utils.importlib import import_module
from django.utils import timezone
import datetime

import cronjobs
from models import CronLock
from django.db import transaction

log = logging.getLogger('cron')

LOCK = getattr(settings, 'CRONJOB_LOCK_PREFIX', 'lock')
LOCK_TIMEOUT = getattr(settings, 'LOCK_TIMEOUT', 5 * 60 * 60)

def run_all_jobs():
    transaction.commit_unless_managed()
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
    for script in registered:
        # Acquire lock if needed.
            if script in cronjobs.registered_lock:
                lock_name = 'django_cron.%s.%s' % (LOCK, script)
                try:
                    cron_locks = CronLock.objects.filter(name=lock_name).order_by("-date_created")
                    lock_count = cron_locks.count()
                    has_lock = False
                    #Remove extraneous locks
                    if lock_count>=1:
                        for lock in cron_locks[1:]:
                            lock.delete()
                        transaction.commit_unless_managed()
                        lock=cron_locks[0]
                        #Remove lock if it has timed out
                        if lock.date_modified < (timezone.now() - datetime.timedelta(seconds=LOCK_TIMEOUT)):
                            lock.delete()
                        else:
                            has_lock = True
                        transaction.commit_unless_managed()

                    if not has_lock:
                        run_single_job(script, registered, )

                except:
                    pass


def run_single_job(script, registered, *args):
    log.info("Beginning job: %s %s" % (script, args))
    registered[script](*args)
    log.info("Ending job: %s %s" % (script, args))
