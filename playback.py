import logging, logging.handlers
import sys

logging.handlers.HTTPHandler('','',method='GET')
logger = logging.getLogger('simple_example') 
http_handler = logging.handlers.HTTPHandler('127.0.0.1:9022', '/event', method='GET') 
logger.addHandler(http_handler)
#logger.setLevel(logging.DEBUG) 

f=open(sys.argv[1])

for i in range(10):
    line = f.readline()
    print line
    logger.critical(line)



## For reference, the exert of the relevant Python logger

# import errno, logging, socket, os, pickle, struct, time, re
# from codecs import BOM_UTF8
# from stat import ST_DEV, ST_INO, ST_MTIME
# import queue
# try:
#     import threading
# except ImportError: #pragma: no cover
#     threading = None

# import http.client, urllib.parse

# port = 9022
# method = "GET"
# host = "127.0.0.1"
# url = "/"

# h = http.client.HTTPConnection(host)
# url = url + "?%s" % (sep, data)



# for item in lines: 
#     data = urllib.parse.urlencode(record)
#     h.putrequest(method, url)
#     h.putheader("Host", host)
#     if method == "POST":
#         h.putheader("Content-type",
#                     "application/x-www-form-urlencoded")
#         h.putheader("Content-length", str(len(data)))
#         h.send(data.encode('utf-8'))
#     h.getresponse()    #can't do anything with the result
