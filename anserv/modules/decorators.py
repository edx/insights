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

funcspecs = [ (['db','params'], 'global'), 
              (['db','user','params'], 'user') ]

def register_handler(cls, category, name, docstring, f):
     if cls not in ['view', 'query']:
         raise ValueError("We can only register views and queries")
     if not name: 
         name = str(f.func_name)
     if not docstring: 
         docstring = str(f.func_doc)
     if not category:
         for (params, cat) in funcspecs:
             if inspect.getargspec(f).args == params:
                 category = cat
     if not category: 
         raise ValueError('Function arguments do not match recognized type. Explicitly set category in decorator.')
     if category not in request_handlers[cls]:
         request_handlers[cls][category]={}
     if name in request_handlers[cls][category]:
         raise KeyError(name+" already in "+category)
     request_handlers[cls][category][name] = {'function': f, 'name': name, 'doc': docstring}

def view(category = None, name = None, docstring = None):
    def view_factory(f):
        register_handler('view',category, name, docstring, f)
        return f
    return view_factory

def query(category = None, name = None, docstring = None):
    ''' 
    ''' 
    def query_factory(f):
        register_handler('query',category, name, docstring, f)
        return f
    return query_factory
