from django.db import transaction
from cronjobs import cron
from django.core.management.base import NoArgsCommand
import time
from django.conf import settings
import logging
log=logging.getLogger(__name__)

CRON_SLEEP_TIME = getattr(settings, 'CRON_SLEEP_TIME', 10)
class Command(NoArgsCommand):
    """
    Run registered cron jobs
    """

    def handle_noargs(self, **options):

        while True:
            try:
                jobs_run = cron.run_all_jobs()
            except:
                log.exception("Could not run cron jobs.")
            transaction.commit_unless_managed()
            log.debug("Ran {0} jobs.".format(jobs_run))
            time.sleep(CRON_SLEEP_TIME)
