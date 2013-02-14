import logging
import imp

from django.conf import settings
from django.utils.importlib import import_module
from django.utils import timezone
from an_evt import views as an_views

import cronjobs
from models import CronLock, CronJob
from django.db import transaction
import datetime

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
            imp.find_module('user_stats', app_path)
        except ImportError as e:
            continue

        import_module('%s.user_stats' % app)

    registered = cronjobs.registered
    parameters = cronjobs.parameters
    log.debug(registered)
    jobs_run = 0
    job_created = False
    for script in registered:
        lock_name = 'django_cron.%s.%s' % (LOCK, script)

        #Get metadata about job
        job_data = CronJob.objects.filter(name=lock_name).order_by("date_created")
        job_data_count = job_data.count()
        if job_data_count >=1:
            remove_locks(job_data[1:])
            job_data = job_data[0]
        else:
            job_data = CronJob(
                name = lock_name,
                time_between_runs = 100,
            )
            job_data.save()
            job_created = True

        #Check if job needs to run
        if job_data.date_modified < (timezone.now() - datetime.timedelta(seconds=job_data.time_between_runs)) or job_created:
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
                try:
                    run_single_job(registered[script], parameters[script])
                    jobs_run+=1
                    job_data.save()
                except:
                    log.error("Failed to run job {0} with params {1}".format(script, parameters[script]))
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

def run_single_job(f, params):
    log.info("Beginning job: %s %s" % (f,params))
    db = an_views.get_database(f)
    f(db, params)
    log.info("Ending job: %s %s" % (f, params))
