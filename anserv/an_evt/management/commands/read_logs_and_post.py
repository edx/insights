import os
import time
from multiprocessing import Pool
from django.conf import settings
import requests

from django.core.management.base import NoArgsCommand

log_files = os.path.listdir(settings.LOG_READ_DIRECTORY)

class Command(NoArgsCommand):
    """
    Run registered cron jobs
    """

    def handle_noargs(self, **options):
        length = len(log_files)
        p = Pool(processes=length)
        p.map(handle_single_log_file,[(log_files[i]) for i in xrange(0,length)])

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
            _http_post(line,settings.LOG_POST_URL)

