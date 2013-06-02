### HACK HACK HACK ###
#
# This is a horrible hack to make a render() function for modules.
#
# In the future, each module should run within its own space
# (globals(), locals()), but for now, this kind of works.
#
# This code:
# 1. Looks at the stack to figure out the calling module
# 2. Matches that up to a module in INSTALLED_ANALYTICS_MODULE (based
#    on longest matching path)
# 3. Uses pkg_resources to find the place where templates are
#    stored (this is part of setuptools)
# 4. Renders the template with Mako
#
# I apologize about this code, but the alternative would be to
# ship without this, in which case we'd accrue technical debt
# with each new module written.
#
### HACK HACK HACK ###
#
# This file also has a static file finder for the modules. This is a
# bit less of a hack (although the implementation is still somewhat
# crude), but it sure doesn't belong in core.render.

import atexit
import importlib
import os.path
import shutil
import sys
import tempfile
import traceback

from pkg_resources import resource_filename

from mako.lookup import TemplateLookup
from django.conf import settings


## Code borrowed from mitx/common/lib/tempdir
def mkdtemp_clean(suffix="", prefix="tmp", dir=None):
    """Just like mkdtemp, but the directory will be deleted when the process ends."""
    the_dir = tempfile.mkdtemp(suffix=suffix, prefix=prefix, dir=dir)
    atexit.register(cleanup_tempdir, the_dir)
    return the_dir


def cleanup_tempdir(the_dir):
    """Called on process exit to remove a temp directory."""
    if os.path.exists(the_dir):
        shutil.rmtree(the_dir)

module_directory = getattr(settings, 'MAKO_MODULE_DIR', None)
if module_directory is None:
    module_directory = mkdtemp_clean()

lookups = {}


def lookup(directory):
    if directory in lookups:
        return lookups[directory]
    else:
        l = TemplateLookup(directories=[directory],
                           module_directory=module_directory,
                           output_encoding='utf-8',
                           input_encoding='utf-8',
                           encoding_errors='replace')
        lookups[directory] = l
        return l


def render(templatefile, context, caller=None):
    ''' Render a template within a module.
    1) Figure out the module this is being called from.
    2) Use resource_filename from packagetools to figure out that module's templates directory
    3) Use the mako template engine to render it.

    Hacks:
    1) We are not caching anything. This will cause performance issues for deployment.
    2) The way we inspect the stack is quite messy. We should do this better.
    '''
    stack = traceback.extract_stack()
    if not caller:
        caller_path = os.path.abspath(stack[-2][0])
        # For testing, use: sys.modules.keys() if sys.modules[module] and '__file__' in sys.modules[module].__dict__]#
        analytics_modules = [sys.modules[module] for module in settings.INSTALLED_ANALYTICS_MODULES]
        analytics_modules.sort(key=lambda x: len(os.path.commonprefix([os.path.abspath(x.__file__), os.path.abspath(caller_path)])))
        caller_module = analytics_modules[-1]
        caller_name = caller_module.__name__

    template_directory = os.path.abspath(resource_filename(caller_name, "templates"))
    template = lookup(template_directory).get_template(templatefile)
    return template.render_unicode(**context)

#### Related hack for static files (although this could be de-hackified easily)

from django.contrib.staticfiles.finders import BaseFinder
from django.contrib.staticfiles import utils
from django.core.files.storage import FileSystemStorage


class ModuleStorage(FileSystemStorage):
    ''' Storage which allows static files to live with prefixes in the
    static directory which do not exist in the filesystem. A file can
    exist as /modules/foo/static/bar.html in the source filesystem,
    but as /djmodules/foo/bar.html in the static_files directory.
    '''
    def path(self, name):
        ''' Returns the absolute path to a file, stripping out
        /djmodules/[module] from the beginning. If the system requests
        /djmodules/testmodule/hello.html, this will return
        /home/user/djanalytics/src/modules/testmodule/static/hello.html
        '''
        rootpath = os.path.relpath(os.path.join(name), self.base_url)
        return FileSystemStorage.path(self, rootpath)

    def listdir(self, path):
        ''' Lists a directory, stripping out /djmodules/static from
        the directory (and allowing / and /djmodules to work)
        '''
        if path == "" or path == "/":
            return ["djmodules"], []
        elif path in ["djmodules", "djmodules/", "/djmodules", "/djmodules/"]:
            return [self.base_url.split('/')[1]], []
        else:
            return FileSystemStorage.listdir(self, path)


class ModuleFileFinder(BaseFinder):
    ''' Finds the static files for all installed analytics
    modules. Does magic to put them in the right place in the URL
    space.
    '''
    def __init__(self, apps=None, *args, **kwargs):
        self.static_paths = None
        self.load_static()

    def load_static(self):
        ''' Walk all modules. Find paths. Create Django storages for them (Django's poorman's pyfs).
        '''
        self.module_paths = [(module.split('.')[-1], os.path.abspath(resource_filename(module, "static"))) for module in settings.INSTALLED_ANALYTICS_MODULES]
        self.static_paths = [(module, path, ModuleStorage(path, os.path.join("djmodules", module))) for module, path in self.module_paths]

    def find(self, path, all=False):
        found = []
        for p in self.static_paths:
            s = os.path.join("djmodules", p[0])+'/'
            if path[:len(s)] == s:
                found.append(os.path.join(p[1], path[len(s):]))
                if not all:
                    return found[0]

        return found

    def list(self, ignore_patterns):
        for module, path, storage in self.static_paths:
            for path in utils.get_files(storage, ignore_patterns):
                yield path, storage
