# Create your views here.

from django.http import HttpResponse
import json
from an_evt.models import StudentBookAccesses

def handle_event(request):
    response = json.loads(request.GET['message'])
    print response
    print json.dumps(response, indent=3)
    sba = StudentBookAccesses.objects.filter(username = response["username"])
    if len(sba) == 0:
        sba = StudentBookAccesses()
        sba.username = response["username"]
        sba.count = 0
    else:
        sba=sba[0]
    sba.count = sba.count + 1
    sba.save()
    return HttpResponse( "Success" )

def user_render(request):
    user = request.GET['uid']
    print user

    sba = StudentBookAccesses.objects.filter(username = user)
    if len(sba):
        pages = sba[0].count
    else: 
        pages = 0


    return HttpResponse( "The user " + user + " saw "+str(pages)+" pages!" )
