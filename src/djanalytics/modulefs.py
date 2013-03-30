import json
import os
import os.path

from django.conf import settings

if settings.DJFS['type'] == 'osfs':
    from fs.osfs import OSFS
else: 
    raise AttributeError("Bad filesystem")

def get_osfs(namespace):
    full_path = os.path.join(settings.DJFS['directory_root'], namespace)
    if not os.path.exists(full_path):
        os.makedirs(full_path)
    osfs = OSFS(full_path)
    return osfs

def get_filesystem(namespace):
    ''' Returns a pyfilesystem for static module storage. 

    Unimplemented: The file system will have two additional properties: 
    1) A way to get a URL for a static file download
    2) A way to expire files (so they are automatically destroyed)
    '''
    if settings.DJFS['type'] == 'osfs':
        return get_osfs( namespace )
    else:
        raise AttributeError("Bad filesystem")
