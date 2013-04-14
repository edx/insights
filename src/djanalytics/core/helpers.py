''' This, together with decorators.py, is the entire API intended to
    be used by plug-in modules.
'''

from util import get_cache, get_filesystem, get_database

def get_replica_database(module):
    ''' Get a read-replica database of a different module. At
    present, not a read-replica, but this will change in the
    future. '''
    get_database(module)

def get_replica_filesystem(module):
    ''' Get a read-replica filesystem of a different module. At
    present, not a read-replica, but this will change in the
    future. '''
    get_filesystem(module)

def get_replica_cache(module):
    ''' Get a read-replica cache of a different module. At
    present, not a read-replica, but this will change in the
    future. '''
    return get_cache(module)

