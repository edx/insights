import os
import time
from multiprocessing import Pool
from django.conf import settings
import requests
import logging
import json

log=logging.getLogger(__name__)

from django.core.management.base import NoArgsCommand

class Command(NoArgsCommand):
    """
    Run registered cron jobs
    """

    def handle_noargs(self, **options):
        while True:
            log_files = [ f for f in os.listdir(settings.LOG_READ_DIRECTORY) if os.path.isfile(os.path.join(settings.LOG_READ_DIRECTORY,f)) ]
            length = len(log_files)
            p = Pool(processes=length)
            p.map_async(handle_single_log_file,[os.path.join(settings.LOG_READ_DIRECTORY,log_files[i]) for i in xrange(0,length)]).get(9999999)

def handle_single_log_file(args):

    import logging, logging.handlers
    import sys

    logger = logging.getLogger('simple_example')
    http_handler = logging.handlers.HTTPHandler('127.0.0.1:9022', '/event', method='GET')
    logger.addHandler(http_handler)

    filename = args
    session = requests.session()
    file = open(filename,'r')

    #Find the size of the file and move to the end
    st_results = os.stat(filename)
    st_size = st_results[6]
    file.seek(st_size)

    i=0
    while i<60:
        where = file.tell()
        line = file.readline()
        if not line:
            time.sleep(1)
            file.seek(where)
            i+=1
        else:
            json_dict= line
            #response_text = _http_get(session,settings.LOG_POST_URL,json_dict)
            logger.critical(line)

