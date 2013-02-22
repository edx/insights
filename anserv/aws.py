from settings import *
import json

with open(ENV_ROOT / "env.json") as env_file:
    ENV_TOKENS = json.load(env_file)

with open(ENV_ROOT / "auth.json") as auth_file:
    AUTH_TOKENS = json.load(auth_file)

MIXPANEL_KEY = AUTH_TOKENS.get("MIXPANEL_KEY","")

LOG_READ_DIRECTORY = "/mnt/edx-all-tracking-logs"
DIRECTORIES_TO_READ = ["prod-edx-00{0}".format(i) for i in xrange(0,9)]
MODULE_RESOURCE_STATIC = '/opt/wwc/modules/static/resource'

DEFAULT_DATABASE = AUTH_TOKENS.get("DATABASES",DATABASES)
DATABASES['default'] = DEFAULT_DATABASE['default']
DEBUG = False

ROOT_URLCONF = 'urls'
