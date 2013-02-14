from modules.mixpanel.mixpanel import track_event_mixpanel
from modules.decorators import view, query, event_handler
import re

SINGLE_PAGES_TO_TRACK = ['/', '/dashboard', '/create_account']
REGEX_PAGES_TO_TRACK = ['/course', '/about']
@event_handler()
def single_page_track_event(fs, db, response):
    for resp in response:
        if resp['event_type'] in  SINGLE_PAGES_TO_TRACK:
            user = resp["username"]
            track_event_mixpanel(resp['event_type'],{'user' : user, 'distinct_id' : user})

@event_handler()
def regex_track_event(fs,db,response):
    for rep in response:
        for regex in REGEX_PAGES_TO_TRACK:
            match = re.search(regex, resp['event_type'])
            if match is not None:
                track_event_mixpanel(regex,{'user' : user, 'distinct_id' : user, 'full_url' : resp['event_type']})
