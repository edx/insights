from modules.mixpanel.mixpanel import track_event_mixpanel
from modules.decorators import view, query, event_handler

SINGLE_PAGES_TO_TRACK = ['/', '/dashboard', '/create_account']
@event_handler()
def generic_track_event(fs, db, response):
    if response[0]['event_type'] in  SINGLE_PAGES_TO_TRACK:
        user = response[0]["username"]
        track_event_mixpanel(response[0]['event_type'],{'user' : user, 'distinct_id' : response[0]['ip']})

