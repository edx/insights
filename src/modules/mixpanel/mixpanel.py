"""
Event tracking, currently uses Mixpanel: https://mixpanel.com
"""
TRACK_BASE_URL = "http://api.mixpanel.com/track/?data=%s"
ARCHIVE_BASE_URL = "http://api.mixpanel.com/import/?data=%s&api_key=%s"
ARCHIVE_POST_URL = "http://api.mixpanel.com/import"
TRACK_POST_URL = "http://api.mixpanel.com/track"
import urllib2
import json
import base64
import time
from django.conf import settings
import logging
import requests
import hashlib

log=logging.getLogger(__name__)

TOKEN = getattr(settings, 'MIXPANEL_KEY', None)
from multiprocessing import Process

class EventTracker(object):
    """Simple Event Tracker
    Designed to be generic, but currently uses Mixpanel
    to actually handle the tracking of the events
    """
    def __init__(self, token=None, api_key=None):
        """Create a new event tracker
        :param token: The auth token to use to validate each request
        :type token: str
        """
        self.token = token
        if self.token is None:
            self.token = TOKEN
        self.api_key = api_key

    def track(self, event, properties=None, callback=None, event_list=False):
        """Track a single event
        :param event: The name of the event to track
        :type event: str
        :param properties: An optional dict of properties to describe the event
        :type properties: dict
        :param callback: An optional callback to execute when
          the event has been tracked.
          The callback function should accept two arguments, the event
          and properties, just as they are provided to this function
          This is mostly used for handling Async operations
        :type callback: function
        """

        if not event_list:
            if properties is None:
                properties = {}
            if not properties.has_key("token"):
                properties['token'] = self.token
            if not properties.has_key("time"):
                properties['time'] = int(time.time())
            assert(properties.has_key("distinct_id")), "Must specify a distinct ID"

            try:
                properties['distinct_id'] = hashlib.sha224(properties['distinct_id'].encode('ascii','ignore')).hexdigest()
                properties['user'] = hashlib.sha224(properties['user'].encode('ascii','ignore')).hexdigest()
            except:
                log.exception("Could not hash for some reason: {0}".format(properties['distinct_id']))

            params = {"event": event, "properties": properties}
        else:
            for i in xrange(0,len(event)):
                if event[i]['properties'] is None:
                    event[i]['properties'] = {}
                if not event[i]['properties'].has_key("token"):
                    event[i]['properties']['token'] = self.token
                if not event[i]['properties'].has_key("time"):
                    event[i]['properties']['time'] = int(time.time())
                try:
                    event[i]['properties']['distinct_id'] = hashlib.sha224(event[i]['properties']['distinct_id'].encode('ascii','ignore')).hexdigest()
                    event[i]['properties']['user'] = hashlib.sha224(event[i]['properties']['user'].encode('ascii','ignore')).hexdigest()
                except:
                    log.exception("Could not hash for some reason: {0}".format(event[i]['properties']['distinct_id']))
            params = event

        data = base64.b64encode(json.dumps(params))
        post_data = {
            'data' : params,
            'api_key' : self.api_key
        }
        track_data = {
            'data' : data
        }
        if self.api_key:
            resp = requests.post(ARCHIVE_POST_URL,data = post_data)
            resp.read()
        else:
            if self.token:
                resp = requests.post(TRACK_POST_URL, data=track_data, headers = {'Content-Type': 'application/json'})
            else:
                log.error("Could not find a token to post to mixpanel.  Is MIXPANEL_KEY defined in the settings?")

        if callback is not None:
            callback(event, properties)

    def track_async(self, event, properties=None, callback=None):
        """Track an event asyncrhonously, essentially this runs the track
        event in a new thread
        :param event: The name of the event to track
        :type event: str
        :param properties: An optional dict of properties to describe the event
        :type properties: dict
        :param callback: An optional callback to execute when the event has been
          tracked. The callback function should accept two arguments, the event
          and properties, just as they are provided to this function
        :type callback: function

        :return: Thread object that will process this request
        :rtype: :class:`threading.Thread`
        """
        from threading import Thread
        p = Process(target=self.track, kwargs={
            'event': event,
            'properties': properties,
            'callback': callback
        })
        p.daemon = True
        p.start()
        return True

def track_event_mixpanel(event,properties):
    event_tracker = EventTracker()
    event_tracker.track(event,properties)

def track_event_mixpanel_async(event,properties):
    event_tracker = EventTracker()
    event_tracker.track_async(event,properties)


