from mitx_settings import *
import json

with open(ENV_ROOT / "kpi-mitx-xml-auth.json") as auth_file:
    AUTH_TOKENS = json.load(auth_file)

MODULESTORE = AUTH_TOKENS["MODULESTORE"]
CONTENTSTORE = AUTH_TOKENS['CONTENTSTORE']
