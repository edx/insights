from settings import *

with open(ENV_ROOT / "env.json") as env_file:
    ENV_TOKENS = json.load(env_file)

with open(ENV_ROOT / "auth.json") as auth_file:
    AUTH_TOKENS = json.load(auth_file)

MIXPANEL_KEY = AUTH_TOKENS.get("MIXPANEL_KEY","")
LOG_READ_DIRECTORY = "/mnt/edx-all-tracking-logs"
