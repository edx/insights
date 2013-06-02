'''
This allows djanalytics to have authentication on provided URLs. 

All views are decorated with the @auth decorator. 

The @auth decorator looks at settings.py for a DJA_AUTH setting. The
DJA_AUTH setting maps function names to authentication decorators. For
example, to require all djanalytics URLs to have a login, add the
following to settings.py:

import django.contrib.auth.decorators
DJA_AUTH = { '.*' : django.contrib.auth.decorators.login_required } 

The goal of this is to, for example, be able to add login_required for
views, but some kind of secret key authentication for queries, and
similar. This code has not been integration-tested yet (although it is
likely to be by the time you read this). 

'''

from django.conf import settings
import re

def auth(f):
    ''' Authentication decorator. It will allow all access, unless
    django settings defines a DJA_AUTH parameter. Such a parameter can
    specify a decorator which will handle authentication/authorization. 

    DJA_AUTH is a dictionary mapping regexps to appropriate decorators
    (so it is possible to e.g. use one for views, and a different one
    for queries)
    '''
    try:
        dja = settings.DJA_AUTH
    except AttributeError:
        dja = {}

    for key in dja:
        if re.match(key, f.func_name):
            return dja[key](f)

    return f
