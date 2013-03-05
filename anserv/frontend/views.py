from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

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

