import os
import time
from django.conf import settings
import logging
import json
import logging, logging.handlers
import sys

log=logging.getLogger(__name__)

from django.core.management.base import NoArgsCommand
from datetime import timedelta

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        course_list = json.load(open(settings.COURSE_CONFIG_PATH))
