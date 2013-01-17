# Create your views here.
from django.shortcuts import render
from django.http import HttpResponse


def dashboard(request):
    return render(request, 'analytics-experiments/anserv/dashboard/static/dashboard.html')

