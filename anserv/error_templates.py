from django.http import HttpResponseNotFound, HttpResponseServerError
from mitxmako.shortcuts import render_to_string, render_to_response

def render_404(request):
    return HttpResponseNotFound(render_to_string('templates/404.html', {}))


def render_500(request):
    return HttpResponseServerError(render_to_string('templates/server-error.html', {}))
