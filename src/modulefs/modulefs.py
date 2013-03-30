import json
import os
import os.path
import types

from django.conf import settings

from models import FSExpirations

if settings.DJFS['type'] == 'osfs':
    from fs.osfs import OSFS
elif settings.DJFS['type'] == 'sf3s':
    from fs.s3fs import S3FS
else: 
    raise AttributeError("Bad filesystem")

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

def expire_objects():
    ''' Remove all obsolete objects from the file systems. Untested. '''
    objects = sorted(FSExpirations.expired(), key=lambda x:x.module)
    fs = None
    module = None
    for o in objects:
        if module != o.module:
            fs = get_filesystem(module)
            module = o.module
        if fs.exists(o.filename):
            fs.remove(o.filename)
        o.delete()

def patch_fs(fs, namespace, url_method):
    ''' Patch a filesystem object to add get_url method and
    expire method. 
    ''' 
    def expire(self, filename, seconds, days=0, expire = True):
        ''' Set the lifespan of a file on the filesystem. 

        filename: Name of file
        expire: False means the file will never be removed
        seconds and days give time to expiration. 
        '''
        FSExpirations.create_expiration(cls, namespace, filename, expires, seconds, days=days)

    fs.expire = types.MethodType(expire, fs)
    fs.get_url = types.MethodType(url_method, fs)
    return fs

def get_osfs(namespace):
    full_path = os.path.join(settings.DJFS['directory_root'], namespace)
    if not os.path.exists(full_path):
        os.makedirs(full_path)
    osfs = OSFS(full_path)
    osfs = patch_fs(osfs, namespace, lambda self, filename:os.path.join(settings.DJFS['url_root'], namespace, filename))
    return osfs

def get_s3fs(namespace):
    fullpath = namespace
    if 'prefix' in settings.DJFS: 
        fullpath = os.path.join(settings.DJFS['prefix'], fullpath)
    s3fs = S3FS(settings.DJFS['bucket'], fullpath)
    return s3fs

