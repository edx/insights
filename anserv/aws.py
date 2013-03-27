from settings import *
from mitx_aws import *
import json

with open(ENV_ROOT / "env.json") as env_file:
    ENV_TOKENS = json.load(env_file)

with open(ENV_ROOT / "auth.json") as auth_file:
    AUTH_TOKENS = json.load(auth_file)

MIXPANEL_KEY = AUTH_TOKENS.get("MIXPANEL_KEY","")

LOG_READ_DIRECTORY = "/mnt/edx-all-tracking-logs"
DIRECTORIES_TO_READ = ["prod-edx-00{0}".format(i) for i in xrange(1,2)]

DEFAULT_DATABASE = AUTH_TOKENS.get("DATABASES",DATABASES)
DATABASES['default'] = DEFAULT_DATABASE['default']
DEBUG = False

TIME_BETWEEN_DATA_REGENERATION = datetime.timedelta(days=1)

ROOT_URLCONF = 'urls'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'django_cache'
    }
}
