event_handlers = []

request_handlers = {'view':{}, 'query':{}}

def event_handler(queued=True, per_user=False, single_process=False, per_resource=False, source_queue=None):
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

def view(category, name):
    def view_factory(a):
        ## Register function in the registry
        if category not in request_handlers['view']:
            request_handlers['view'][category]={}
        if name in request_handlers['view'][category]:
            raise KeyError(name+" already in "+category)
        request_handlers['view'][category][name] = a
        
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
