from django.http import HttpResponse

from django.views.decorators.csrf import csrf_exempt

from django.conf import settings
import json, requests, re, sys
import traceback

def print_exception(f):
    def helper(r):
        try: 
            return f(r)
        except:
            print "Unexpected error:", sys.exc_info()
            traceback.print_exc()
            raise
    return helper

@csrf_exempt
def sns(request):
    ''' This view handles SNS requests, and forwards them along to the
    event handler. Valid ARNs for the subscribed SNS channels should
    be specified in settings.py. 

    WARNING: This does not verify SNS signatures. It relies on the
    server sitting behind a firewall where SNS signatures cannot be
    spoofed.
    '''
    body = json.loads(request.raw_post_data)
    # If we receive an attempt to subscribe to SNS, we confirm it is
    # one we'd like to subscribe to, and that the URL is an Amazon SNS
    # URL. We don't know if this is full-proof (probably not); we
    # still count on a firewall to make sure we don't get random
    # requests from the Internet. 
    #
    # We really should verify the signature. This is slightly complex. 
    if body['TopicArn'] not in settings.SNS_SUBSCRIPTIONS:
        raise Exception("Invalid topic ARN; check settings.py")

    if body['Type'] == 'SubscriptionConfirmation':
        url = body['SubscribeURL']
        if not re.compile("^https://sns\.[a-z0-9\-]+\.amazonaws.com/\?Action=ConfirmSubscription\&TopicArn=arn").match(url):
            raise Exception("Invalid SNS URL")
        r = requests.get(url)
    elif body['Type'] == 'Notification':
        message = body['Message']
        subject = body['Subject']
        print message, subject
    else:
        raise Exception("Unknown message type")
        
    return HttpResponse("All Good.")
