from modules.mixpanel.mixpanel import track_event_mixpanel
from modules.decorators import view, query, event_handler
import re
import logging
SINGLE_PAGES_TO_TRACK = ['/', '/dashboard', '/create_account']
COURSE_PAGES_TO_TRACK = ['/courses', '/about']
@event_handler()
def single_page_track_event(fs, db, response):
    for resp in response:
        if resp['event_type'] in  SINGLE_PAGES_TO_TRACK:
            user = resp["username"]
            host = resp['host']
            agent = resp['agent']
            track_event_mixpanel(resp['event_type'],{'user' : user, 'distinct_id' : user, 'host' : host, 'agent' : agent})

@event_handler()
def course_track_event(fs,db,response):
    for resp in response:
        for regex in COURSE_PAGES_TO_TRACK:
            match = re.search(regex, resp['event_type'])
            user = resp["username"]
            if match is not None:
                split_url = resp['event_type'].split("/")
                org = split_url[2]
                course = split_url[3]
                host = resp['host']
                agent = resp['agent']
                track_event_mixpanel(regex,{'user' : user, 'distinct_id' : user, 'full_url' : resp['event_type'], 'course' : course, 'org' : org, 'host' : host, 'agent' : agent})
