# Generates a dummy event for testing
# E.g.:
# 
#    python sendevent.py localhost:8020 /httpevent actor=bob action=submitanswer object=problem5

import json
import sys
import logging
from logging.handlers import HTTPHandler

logger=logging.getLogger('sendevent')
logger.addHandler(HTTPHandler(sys.argv[1], sys.argv[2]))
objects=[o.split("=") for o in sys.argv[3:]]
logger.error(json.dumps(dict(objects)))
