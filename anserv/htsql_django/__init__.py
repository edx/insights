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

engine = getattr(settings, 'DATABASES', {})
engine = engine['default']

engine_val = {
    'sqlite3' : 'sqlite',
    'mysql' : 'mysql',
}

engine_string = engine["ENGINE"].split(".")[3]
instance_config = {
    'engine' : engine_val[engine_string],
    'username' : engine['USER'],
    'password' : engine['PASSWORD'],
    'host' : engine['HOST'],
    'port' : engine['PORT'],
    'database' : engine['NAME']
}

if instance_config['engine'] == "sqlite":
    instance_config['database'] = os.path.abspath(instance_config['database'])

if isinstance(instance_config['port'], basestring):
    try:
        instance_config['port'] = int(instance_config['port'])
    except:
        instance_config['port'] = 0

log.debug(instance_config)
log.debug(CONFIG)
log.debug(DEFAULT_CONFIG)

instance = HTSQL(instance_config, CONFIG, DEFAULT_CONFIG)
produce = instance.produce

