# Create your views here.
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse


def dashboard(request):
    if request.user.is_authenticated():
        return render(request, 'analytics-experiments/anserv/dashboard/static/dashboard.html')
    else:
       return HttpResponseRedirect(reverse("django.contrib.auth.views.login"))

