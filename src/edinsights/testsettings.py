# This settings file is used for testing cron (periodic tasks)

from settings import *

CELERY_IMPORTS = ()
# CELERY_IMPORTS += ('core.testtasks',)
CELERY_IMPORTS += ('core.tests',)