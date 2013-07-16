
# required for queuing new tasks but does not store results
BROKER_URL = 'mongodb://localhost/celery'

# required for storing results (might be unnecessary)
CELERY_RESULT_BACKEND = 'mongodb://localhost/celeryresult'

#
CELERY_TASK_RESULT_EXPIRES = 60 * 60 #1 hour