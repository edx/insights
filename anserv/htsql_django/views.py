#
# Copyright (c) 2006-2013, Prometheus Research, LLC
#

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.db import transaction
from . import instance

def to_environ(request):
    environ = request.META.copy()
    prefix = reverse(gateway)
    if prefix.endswith('/'):
        prefix = prefix[:-1]
    if isinstance(environ['PATH_INFO'], unicode):
        environ['PATH_INFO'] = environ['PATH_INFO'].encode('utf-8')
    if isinstance(environ['SCRIPT_NAME'], unicode):
        environ['SCRIPT_NAME'] = environ['SCRIPT_NAME'].encode('utf-8')
    assert environ['PATH_INFO'].startswith(prefix)
    assert environ['SCRIPT_NAME'] == ''
    environ['SCRIPT_NAME'] = prefix
    environ['PATH_INFO'] = environ['PATH_INFO'][len(prefix):]
    return environ

@login_required
def gateway(request):
    class output:
        status = None
        headers = None
        body = None
    environ = to_environ(request)
    def start_response(status, headers, exc_info=None):
        output.status = status
        output.headers = headers
    output.body = ''.join(instance(environ, start_response))
    response = HttpResponse(output.body, status=int(output.status.split()[0]))
    for header, value in output.headers:
        response[header] = value
    return response

