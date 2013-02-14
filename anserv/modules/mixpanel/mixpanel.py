"""
Event tracking, currently uses Mixpanel: https://mixpanel.com
"""
TRACK_BASE_URL = "http://api.mixpanel.com/track/?data=%s"
ARCHIVE_BASE_URL = "http://api.mixpanel.com/import/?data=%s&api_key=%s"
import urllib2
import json
import base64
import time
from django.conf import settings

TOKEN = settings.MIXPANEL_KEY

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

    def track(self, event, properties=None, callback=None):
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
        if properties is None:
            properties = {}
        if not properties.has_key("token"):
            properties['token'] = self.token
        if not properties.has_key("time"):
            properties['time'] = int(time.time())

        assert(properties.has_key("distinct_id")), "Must specify a distinct ID"

        params = {"event": event, "properties": properties}
        data = base64.b64encode(json.dumps(params))
        if self.api_key:
            resp = urllib2.urlopen(ARCHIVE_BASE_URL % (data, self.api_key))
        else:
            resp = urllib2.urlopen(TRACK_BASE_URL % data)
        resp.read()

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
        t = Thread(target=self.track, kwargs={
            'event': event,
            'properties': properties,
            'callback': callback
        })
        t.start()
        return t

def track_event_mixpanel(event,properties):
    event_tracker = EventTracker()
    event_tracker.track(event,properties)


