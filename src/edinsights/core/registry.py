import inspect
import logging

log=logging.getLogger(__name__)

event_handlers = []
request_handlers = {'view':{}, 'query':{}}

from edinsights.core.util import default_optional_kwargs
funcskips = default_optional_kwargs.keys()+['params'] # params are additional GET/POST parameters

def register_handler(cls, category, name, description, f, args):
    ''' Helper function for @view and @query decorators. 
    '''
    log.debug("Register {0} {1} {2} {3}".format(cls, category, name, f))
    # Figure out where this goes. See if there are parameters, and if not, 
    # create them by inspecting the function. 
    if args == None:
        args = inspect.getargspec(f).args
    if cls not in ['view', 'query']:
        raise ValueError("We can only register views and queries")
    if not name:
        name = str(f.func_name)
    if not description:
        description = str(f.func_doc)
    if not category:
        url_argspec = [a for a in inspect.getargspec(f).args if a not in funcskips]
        category=""
        for i in xrange(0,len(url_argspec)):
            spec = url_argspec[i]
            category += "{0}".format(spec)
            if i!= len(url_argspec) -1:
                category+="+"
    if cls not in request_handlers:
        request_handlers[cls] = {}

    # We may want to register under multiple names. E.g. 
    # edx.get_grades and (once adopted globally) generic 
    # get_grades
    if isinstance(name, list):
        names = name
    else:
        names = [name]
    for n in names: 
        if n in request_handlers[cls]:
            # We used to have this be an error.
            # We changed to a warning for the way we handle dummy values.
            log.warn("{0} already in {1}".format(n, category))  # raise KeyError(name+" already in "+category)

        request_handlers[cls][n] = {'function': f, 'name': n, 'doc': description, 'category' : category}

class StreamingEvent:
    ''' Event object. Behaves like the normal JSON event dictionary,
    but allows modules to add additional properties. JSON properties
    are gotten with [] (which should be minimally used), while derived
    properties with . For example, a tincan module could add: 

    evt.agent
    evt.verb
    evt.object

    Using these would allow modules to continue working even with
    schema changes (or using this framework with LMSes with different
    event structures).

    It is also immutable. 
    '''
    def __init__(self, event):
        if isinstance(event,str) or isinstance(event,unicode):
            event = json.loads(event)
        self.event = event

    def __contains__(self, key):
        return key in self.event

    def __getitem__(self, key):
        return self.event[key]

    def __getattr__(self, key):
        if key in event_property_registry:
            return event_property_registry[key]['function'](self)
        else: 
            raise AttributeError("StreamingEvent has no attribute "+key)

    def __str__(self):
        return "Event:"+self.event.__str__()

    def __repr__(self):
        return "Event:"+self.event.__repr__()

    def keys(self):
        return self.event.keys()

event_property_registry = {}
def register_event_property(f, name, description):
    ''' helper for event_property decorator '''
    if not name:
        name = str(f.func_name)
    if not description:
        description = str(f.func_doc)
    event_property_registry[name] = {'function': f, 'name': name, 'doc': description}

def schema_helper():
    ''' Return all endpoints (returned in a format identical to schema view)
    '''
    endpoints = []
    for cls in request_handlers:
        for name in request_handlers[cls]:
            rh = request_handlers[cls][name]
            endpoints.append({'category' : rh['category'], 'class': cls, 'name' : name, 'doc' : rh['doc']})
    return endpoints

def handle_request(cls, name, **kwargs):
    ''' Generic code to handle views and requests '''
    args = dict()
    categories = request_handlers[cls]
    if name in categories: 
        handler_dict = categories[name]
    else:
        raise Http404(name+"  is not a valid function")
    handler = handler_dict['function']
    if 'args' in handler_dict:
        arglist = handler_dict['arglist']
    else:
        arglist = inspect.getargspec(handler).args

    from util import optional_parameter_call
    return optional_parameter_call(handler, kwargs, arglist)

