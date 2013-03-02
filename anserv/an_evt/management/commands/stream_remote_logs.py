import os
import time
from multiprocessing import Pool
from django.conf import settings
import requests
import logging
import json

log=logging.getLogger(__name__)

from django.core.management.base import NoArgsCommand

log_commands = [
    'ssh sandbox-mit-002.m.edx.org "sudo tail -F /mnt/logs/tracking.log" > /home/vik/mitx_all/analytics-logs/sandbox-mit.log',
    'ssh sandbox-vik-001.m.edx.org "sudo tail -F /mnt/logs/tracking.log" > /home/vik/mitx_all/analytics-logs/sandbox-vik.log',
]

class Command(NoArgsCommand):
    """
    Run registered cron jobs
    """

    def handle_noargs(self, **options):
        length = len(log_commands)
        p = Pool(processes=length)
        p.map_async(handle_single_log_command,[log_commands[i] for i in xrange(0,length)]).get(9999999)

def handle_single_log_command(args):

    import logging, logging.handlers
    import sys
    import subprocess

    shell_command = args
    subprocess.call(shell_command, shell=True)


