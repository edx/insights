import json
import os
import os.path

from django.conf import settings

if settings.DJFS['type'] == 'osfs':
    from fs.osfs import OSFS
elif settings.DJFS['type'] == 'sf3s':
    from fs.s3fs import S3FS
else: 
    raise AttributeError("Bad filesystem")

def set_expiry(fs, namespace, filename, time):
    pass

def patch_fs(fs, url_method):
    ''' Patch a filesystem object to add get_url method and
    expire method. 
    ''' 
    return fs

def get_osfs(namespace):
    full_path = os.path.join(settings.DJFS['directory_root'], namespace)
    if not os.path.exists(full_path):
        os.makedirs(full_path)
    osfs = OSFS(full_path)
    return osfs

def get_s3fs(namespace):
    fullpath = namespace
    if 'prefix' in settings.DJFS: 
        fullpath = os.path.join(settings.DJFS['prefix'], fullpath)
    s3fs = S3FS(settings.DJFS['bucket'], fullpath)
    return s3fs

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
