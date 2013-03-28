from modules.mixpanel.mixpanel import track_event_mixpanel, track_event_mixpanel_async
from modules.decorators import view, query, event_handler
from modules.tasks import track_event_mixpanel_batch
import re
import logging
log=logging.getLogger(__name__)
from multiprocessing import Pool
import time
from dateutil import parser
import json

SINGLE_PAGES_TO_TRACK = ['/', '/dashboard', '/create_account', 'page_close']
COURSE_PAGES_TO_TRACK = ['/about']  #'/courses', Dont track courses because it is an insane amount of hits
VIDEO_EVENTS_TO_TRACK = ['play_video', 'pause_video']
PROBLEM_EVENTS_TO_TRACK = ['problem_check', 'problem_show', 'show_answer', 'save_problem_check', 'reset_problem']
BOOK_EVENTS_TO_TRACK = ['book']
OPEN_ENDED_EVENTS_TO_TRACK = ['rubric_select', 'oe_staff_grading_show_problem', 'oe_peer_grading_show_problem',
                              'oe_staff_grading_hide_problem', 'oe_peer_grading_hide_problem', 'oe_show_full_feedback',
                              'oe_show_respond_to_feedback', 'oe_feedback_response_selected'
                              ]

def extract_course_and_org(event_data):
    org = None
    course = None
    name = None
    if 'event' in event_data:
        try:
            ev_data = event_data['event']
            try:
                ev_data = json.loads(ev_data)
            except:
                pass
            if isinstance(ev_data, dict):
                if 'problem_id' in ev_data:
                    split_data = ev_data['problem_id'].split('/')
                    org = split_data[2]
                    course = split_data[3]
                    name = split_data[5]
                elif 'id' in ev_data:
                    split_data = ev_data['id'].split('-')
                    org = split_data[1]
                    course = split_data[2]
                    name = split_data[4]
            elif isinstance(ev_data,basestring):
                split_data = ev_data.split('-')
                org = split_data[2]
                course = split_data[3]
                name = split_data[5]
        except:
            log.exception("Could not parse json.")
            pass

    return org,course,name

@event_handler()
def single_page_track_event(fs, db, response):
    mixpanel_data = []
    for resp in response:
        try:
            if resp['event_type'] in  SINGLE_PAGES_TO_TRACK + BOOK_EVENTS_TO_TRACK + PROBLEM_EVENTS_TO_TRACK + VIDEO_EVENTS_TO_TRACK + OPEN_ENDED_EVENTS_TO_TRACK:
                user = resp["username"]
                host = resp['host']
                agent = resp['agent']
                time_data = extract_time(resp)
                org, course, name = extract_course_and_org(resp)
                event_data = {'event' : resp['event_type'],'properties' : {'user' : user, 'distinct_id' : user, 'host' : host, 'agent' : agent, 'time' : time_data}}
                if org is not None:
                    event_data['properties'].update({
                        'org' : org,
                        'course' : course,
                        'name' : name,
                    })
                mixpanel_data.append(event_data)
        except:
            log.exception("Mixpanel single page track failed")
    track_event_mixpanel_batch.delay(mixpanel_data)

@event_handler()
def course_track_event(fs,db,response):
    mixpanel_data =[]
    for resp in response:
        try:
            for regex in COURSE_PAGES_TO_TRACK:
                match = re.search(regex, resp['event_type'])
                user = resp["username"]
                if match is not None:
                    split_url = resp['event_type'].split("/")
                    org = split_url[2]
                    course = split_url[3]
                    host = resp['host']
                    agent = resp['agent']
                    time_data = extract_time(resp)
                    mixpanel_data.append({'event': regex,'properties' : {'user' : user, 'distinct_id' : user, 'full_url' : resp['event_type'], 'course' : course, 'org' : org, 'host' : host, 'agent' : agent, 'time' : time_data}})
        except:
            log.exception("Mixpanel course track failed.")
    track_event_mixpanel_batch.delay(mixpanel_data)

def run_posts_async(data):
    num_to_post = len(data)
    num_processes = min([100,num_to_post])
    p = Pool(processes=num_processes)
    p.map_async(track_event_mixpanel_async,[(data[i][0],data[i][1]) for i in xrange(0,num_to_post)]).get(9999999)

def extract_time(resp):
    try:
        time_data = resp['time']
        time_data = parser.parse(time_data)
        time_data = time.mktime(time_data.timetuple())
    except:
        time_data = int(time.time())
        log.error("Could not parse time {0}".format(resp['time']))

    return time_data


