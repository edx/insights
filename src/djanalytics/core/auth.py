'''
This allows djanalytics to have authentication on provided URLs. 

All views are decorated with the @auth decorator. 

The @auth decorator looks at settings.py for a DJA_AUTH setting. The
DJA_AUTH setting maps function names to authentication decorators. For
example, to require all djanalytics URLs to have a login, add the
following to settings.py:

import django.contrib.auth.decorators
DJA_AUTH = { '.*' : django.contrib.auth.decorators.login_required } 

'''

from django.conf import settings
import re

def auth(f):
    if 'DJA_AUTH' in settings.__dir__():
        dja = settings.DJA_AUTH
    else:
        dja = {}

    for key in dja:
        if re.match(key, f.func_name):
            return dja[key](f)

    return f
