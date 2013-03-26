import os
import time
from django.conf import settings
import logging
import json
import logging, logging.handlers
import sys
import subprocess

log=logging.getLogger(__name__)

from django.core.management.base import NoArgsCommand
from datetime import timedelta

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        course_list = json.load(open(settings.COURSE_CONFIG_PATH))
        for course in course_list:
            try:
                self.pull_single_course(course, course_list[course])
            except:
                log.exception("Could not pull course {0}".format(course))

    def pull_single_course(self, course_dir, course_repo):
        course_path = os.path.join(settings.COURSE_FILE_PATH, course_dir)
        log.debug(settings.COURSE_FILE_PATH)
        if not os.path.isdir(course_path):
            #subprocess.call(["mkdir", course_path], cwd=settings.COURSE_FILE_PATH)
            subprocess.call("git clone {0} {1}".format(settings.GIT_CLONE_URL.format(course_repo), course_dir), cwd=settings.COURSE_FILE_PATH, shell=True)
        else:
            subprocess.call("git pull", cwd=course_path, shell=True)

