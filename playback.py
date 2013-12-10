import logging, logging.handlers
import sys

logging.handlers.HTTPHandler('','',method='GET')
logger = logging.getLogger('simple_example') 
http_handler = logging.handlers.HTTPHandler('127.0.0.1:8002', '/httpevent', method='GET') 
logger.addHandler(http_handler)

f=open(sys.argv[1])
for line in f:
    logger.critical(line)

