import logging
import imp
import os

from django.conf import settings
from django.utils.importlib import import_module
from django.utils import timezone
from an_evt import views as an_views

import cronjobs
from models import CronLock
from django.db import transaction

log = logging.getLogger('cron')

LOCK = getattr(settings, 'CRONJOB_LOCK_PREFIX', 'lock')
LOCK_TIMEOUT = getattr(settings, 'LOCK_TIMEOUT', 5 * 60 * 60)
MODULE_EXTENSIONS = ('.py', '.pyc', '.pyo')

def run_all_jobs():
    transaction.commit_unless_managed()
    for app in settings.INSTALLED_APPS:
        try:
            app_path = import_module(app).__path__
        except AttributeError:
            continue        
        module_set = set([os.path.splitext(module)[0] for module in os.listdir([0]app_path) if module.endswith(MODULE_EXTENSIONS)])
        for module in module_set:
            try:
                import_module("{0}.{1}".format(app,module))
            except ImportError as e:
                continue

    registered = cronjobs.registered
    log.debug(registered)
    jobs_run = 0
    for script in registered:
        lock_name = 'django_cron.%s.%s' % (LOCK, script)
        # Acquire lock if needed.
        has_lock = False
        if script in cronjobs.registered_lock:
            try:
                cron_locks = get_all_locks(lock_name)
                lock_count = cron_locks.count()

                #Remove extraneous locks
                if lock_count>=1:
                    remove_locks(cron_locks[1:])
                    lock = cron_locks[0]
                    #Remove lock if it has timed out
                    if lock.date_modified < (timezone.now() - datetime.timedelta(seconds=LOCK_TIMEOUT)):
                        lock.delete()
                    else:
                        has_lock = True
                    transaction.commit_unless_managed()

                if not has_lock:
                    create_lock(lock_name)
            except:
                log.exception("Could not modify locks correctly.")
        if not has_lock:
            run_single_job(script, registered)
            jobs_run+=1

            remove_locks(get_all_locks(lock_name))

    return jobs_run

def create_lock(lock_name):
    lock = CronLock(
        name=lock_name
    )
    lock.save()

def get_all_locks(lock_name):
    cron_locks = CronLock.objects.filter(name=lock_name).order_by("-date_created")
    return cron_locks

def remove_locks(cron_locks):
    for lock in cron_locks:
        lock.delete()

def run_single_job(script, registered, *args):
    log.info("Beginning job: %s %s" % (script, args))
    db = an_views.get_database(registered[script])
    registered[script](db, *args)
    log.info("Ending job: %s %s" % (script, args))
