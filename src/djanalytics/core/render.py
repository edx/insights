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
        l = TemplateLookup(directories = [directory], 
                           module_directory = module_directory, 
                           output_encoding='utf-8',
                           input_encoding='utf-8',
                           encoding_errors='replace')
        lookups[directory] = l
        return l

def render(templatefile, context, caller = None):
    stack = traceback.extract_stack()
    if not caller: 
        caller_path = os.path.abspath(stack[-2][0])
        # For testing, use: sys.modules.keys() if sys.modules[module] and '__file__' in sys.modules[module].__dict__]# 
        analytics_modules = [sys.modules[module] for module in settings.INSTALLED_ANALYTICS_MODULES] 
        analytics_modules.sort(key = lambda x : len(os.path.commonprefix([x.__file__, os.path.abspath(caller_path)])))
        caller_module = analytics_modules[-1]
        caller_name = caller_module.__name__

    template_directory = os.path.abspath(resource_filename(caller_name, "templates"))

    print "Caller, ", template_directory
    template = lookup(template_directory).get_template(templatefile)
    return template.render_unicode(**context)
    return "Hello!"

