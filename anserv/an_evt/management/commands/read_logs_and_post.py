import os
import time
from multiprocessing import Pool
from django.conf import settings
import requests
import logging
import json

log=logging.getLogger(__name__)

from django.core.management.base import NoArgsCommand

log_files = [ f for f in os.listdir(settings.LOG_READ_DIRECTORY) if os.path.isfile(os.path.join(settings.LOG_READ_DIRECTORY,f)) ]

class Command(NoArgsCommand):
    """
    Run registered cron jobs
    """

    def handle_noargs(self, **options):
        length = len(log_files)
        p = Pool(processes=length)
        p.map_async(handle_single_log_file,[os.path.join(settings.LOG_READ_DIRECTORY,log_files[i]) for i in xrange(0,length)]).get(9999999)

def _http_post(session, url, data, timeout):
    '''
    Contact grading controller, but fail gently.
    Takes following arguments:
    session - requests.session object
    url - url to post to
    data - dictionary with data to post
    timeout - timeout in settings

    Returns (success, msg), where:
        success: Flag indicating successful exchange (Boolean)
        msg: Accompanying message; Controller reply when successful (string)
    '''

    try:
        r = session.post(url, data=data, timeout=timeout, verify=False)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        log.error('Could not connect to server at %s in timeout=%f' % (url, timeout))
        return (False, 'Cannot connect to server.')

    if r.status_code not in [200]:
        log.error('Server %s returned status_code=%d' % (url, r.status_code))
        return (False, 'Unexpected HTTP status code [%d]' % r.status_code)
    return (True, r.text)

def _http_get(session, url, data={}):
    """
    Send an HTTP get request:
    session: requests.session object.
    url : url to send request to
    data: optional dictionary to send
    """
    try:
        r = session.get(url, params=data)
    except requests.exceptions.ConnectionError, err:
        log.error(err)
        return (False, 'Cannot connect to server.')

    if r.status_code not in [200]:
        return (False, 'Unexpected HTTP status code [%d]' % r.status_code)
    return r.text


def handle_single_log_file(args):
    filename = args
    session = requests.session()
    file = open(filename,'r')

    #Find the size of the file and move to the end
    st_results = os.stat(filename)
    st_size = st_results[6]
    file.seek(st_size)

    while True:
        where = file.tell()
        line = file.readline()
        if not line:
            time.sleep(1)
            file.seek(where)
        else:
            log.debug("Posting {0}".format(line))
            json_dict= {'message' : json.dumps(line)}
            response_text = _http_get(session,settings.LOG_POST_URL,json_dict)

