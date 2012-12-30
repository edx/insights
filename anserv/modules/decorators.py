import inspect

event_handlers = []

request_handlers = {'view':{}, 'query':{}}

def event_handler(queued=True, per_user=False, per_resource=False, single_process=False, source_queue=None):
    ''' Decorator to register an event handler. 

    queued=True ==> Normal mode of operation. Cannot break system (unimplemented)
    queued=False ==> Event handled immediately operation. Slow handlers can break system. 

    per_user = True ==> Can be sharded on a per-user basis (default: False)
    per_resource = True ==> Can be sharded on a per-resource basis (default: False)

    single_process = True ==> Cannot be distributed across process/machines. Queued must be true. 
    
    source_queue ==> Not implemented. For a pre-filter (e.g. video)
    '''

    if single_process or source_queue or queued:
        raise NotImplementedError("Framework isn't done. Sorry. queued=False, source_queue=None, single_proces=False")
    def event_handler_factory(func):
        event_handlers.append(func)
        return func
    return event_handler_factory

def view(category = None, name = None, docstring = None):
    def view_factory(a):
        ## Register function in the registry
        registered_name = name
        doc = docstring
        cat = category
        if not registered_name:
            registered_name = str(a.func_name)
        if not doc: 
            doc = str(a.func_doc)

        if not cat:
            if inspect.getargspec(a).args == ['db','params']:
                cat = 'global'
            else:
                raise ValueError('Function arguments do not match recognized type. Explicitly set category in decorator.')

        if cat not in request_handlers['view']:
            request_handlers['view'][cat]={}
        if registered_name in request_handlers['view'][cat]:
            raise KeyError(registered_name+" already in "+cat)
        request_handlers['view'][cat][registered_name] = {'function': a, 'name': registered_name, 'doc': doc}
        return a
    return view_factory

def query(category, name):
    ''' 
    ''' 
    def query_factory(a):
        ## Register function in the registry
        if category not in request_handlers['query']:
            request_handlers['query'][category]={}
        if name in request_handlers['query'][category]:
            raise KeyError(name+" already in "+category)
        request_handlers['query'][category][name] = a
        
        return a
    return query_factory
