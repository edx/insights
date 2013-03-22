#
# Copyright (c) 2006-2013, Prometheus Research, LLC
#

from htsql import HTSQL
from django.conf import settings
import logging
import os

log= logging.getLogger(__name__)

CONFIG = getattr(settings, 'HTSQL_CONFIG', {})
DEFAULT_CONFIG = {
        'tweak.django': {},
}

instance = HTSQL(None, CONFIG, DEFAULT_CONFIG)
produce = instance.produce

