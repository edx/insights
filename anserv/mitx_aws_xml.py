import json
from mitx_aws import *

with open(ENV_ROOT / "kpi-mitx-xml-auth.json") as auth_file:
    AUTH_TOKENS = json.load(auth_file)

MODULESTORE = AUTH_TOKENS["MODULESTORE"]
CONTENTSTORE = AUTH_TOKENS['CONTENTSTORE']
