from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.conf import settings
import os
import logging

log=logging.getLogger(__name__)

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            return HttpResponseRedirect("/essay_site/api/v1/?format=json")
    else:
        form = UserCreationForm()
    return render_to_response("registration/register.html", RequestContext(request,{
        'form': form,
        }))

@login_required
def protected_data(request, **params):
    path = params.get("path", None)
    if path is None:
        path = request.GET.get('path', None)
    response = HttpResponse()
    del response['content-type']
    log.debug(str(os.path.join(settings.PROTECTED_DATA_ROOT, path)))
    response['X-Accel-Redirect'] = str(os.path.join(settings.PROTECTED_DATA_ROOT, path))
    return response

