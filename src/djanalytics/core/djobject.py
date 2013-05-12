''' This is a generic interface to djanalytics. It presents views,
etc. as Python objects. 

This is prototype-grade code. 

It is very ugly. It will be cleaned up, but still slightly ugly,
however. I'm not sure if there is a good way to make this clean, but
the ugliness here will save a lot of ugliness for the API caller.
'''

import decorator
import inspect
import json
import requests
import urllib

def http_rpc_helper(baseurl, view_or_query, function, headers = {}, timeout = None):
    ''' Make an RPC call to a remote djanalytics instance
    '''
    if baseurl: 
        baseembedurl = baseurl+view_or_query+"/"

    def rpc_call(**kwargs):
        url = urllib.basejoin(baseembedurl, function)
        if kwargs:
            url = url+"?"+urllib.urlencode(kwargs)
        kwargs = {}
        if headers: 
            kwargs['headers'] = headers
        if timeout: 
            kwargs['timeout'] = float(timeout)
        response = requests.get(url, **kwargs)
        if response.status_code == 200:
            return response.content
        if response.status_code == 404:
            raise AttributeError(function)
        error = "Error calling {func} {status}".format(func=function, status=response.status_code)
        raise Exception(error)
    return rpc_call

def local_call_helper(view_or_query, function):
    ''' Make a call (functionally identical to RPC) to the local djanalytics instance
    '''
    import djanalytics.core.registry
    def rpc_call(**kwargs):
        return djanalytics.core.registry.handle_request(view_or_query, function, **kwargs)
    return rpc_call

class multi_embed():
    ''' Lets you merge multiple embeds into one. E.g. talk to 5
    analytics servers.

    This code is scaffolding meant to define the interface. It is
    untested.

    '''
    def __init__(self, embeds):
        self._embeds = embeds
    def __getattr__(self, attr):
        print ">>>>>>>>>>>>> Getting", attr
        for x in self._embeds:
            f = None
            try:
                f = x.__getattr__(attr)
            except AttributeError:
                pass
            if f:
                print
                print ">>>>>>>>>>>>>>>>>>>", f
                print
                return f
        print "Not found"
        raise AttributeError(attr)

    def _refresh_schema(self):
        for x in self._embeds:
            x._refresh_schema
    def __dir__(self):
        child_dirs = [x.__dir__() for x in self._embeds]
        print child_dirs
        return sorted(list(set(sum(child_dirs, []))))
    def __repr__(self):
        return "/".join(map(lambda x:repr(x), self._embeds))

class single_embed(object):
    def __init__(self, view_or_query, baseurl = None, headers = {}):
        self._schema = None
        self._baseurl = baseurl
        self._view_or_query = view_or_query
        self._headers = headers
        self._refresh_schema()
        self._timeout = [ None ]
        class MetaEmbed(object):
            ''' Allows operations on the view or query through view.meta. 
            E.g. view.meta.set_timeout(t)
            
            This code is scaffolding meant to define the interface. It
            is untested.
            '''
            def __init__(self, embed):
                self._embed = embed
            def set_timout(self, t):
                ''' Set the timeout for object if it is going over a
                network. Timeouts are kept on a stack; when you're
                done, call unset_timeout, to return the timeout to
                where it was. '''
                self._embed._timeout.append(t)
            def unset_timeout(self):
                ''' Unset the timeout for object. See set_timeout for
                details.  '''
                self._embed._timeout.pop()

        self.meta = MetaEmbed(self)

    def _find_in_schema(self, cls = None, name = None):
        ''' Search for a given class/name combo in schema. Return all
        matching objects. Either can be passed alone. 
        ''' 
        items = []
        for item in self._schema: 
            if cls and item['class'] != cls: 
                continue
            if name and item['name'] != name: 
                continue
            items.append(item)
        return items

    def _refresh_schema(self):
        if not self._schema:
            if self._baseurl:
                url = self._baseurl+"schema"
                self._schema = json.loads(requests.get(url).content)
            else: 
                import djanalytics.core.registry
                self._schema = djanalytics.core.registry.schema_helper()

    def __getattr__(self, attr):
        ## Disallow internal. This is necessary both for analytics,
        ## and for Python. Otherwise, we have all sorts of __setattr__
        ## and similar overwritten
        if attr[0] == '_':
            return

        # Return a caller to the function
        if self._baseurl:
            helper = http_rpc_helper(self._baseurl, self._view_or_query, attr, 
                                     headers = self._headers, timeout = self._timeout[-1])
        else:
            helper = local_call_helper(self._view_or_query, attr)
            
        # Modified the function to have the proper function spec. 
        # The internals of decorator.FunctionMaker make me sick. 
        try: 
            rpcspec = self._find_in_schema(cls = self._view_or_query, name = attr)[0]
        except IndexError: 
            raise AttributeError(attr)
        category = rpcspec['category']

        # TODO: Category should be a list, not a string
        def_params = category.replace('+',',') # Is this still needed? 
        if def_params:
            call_params = ",".join(["{p}={p}".format(p=p) for p in category.split('+')])
        else:
            call_params = ""
        funcspec = "{name}({params})".format(name='rpc_'+attr, 
                                             params=def_params)
        callspec = "return helper({params})".format(params=call_params)
        return decorator.FunctionMaker.create(funcspec, 
                                              callspec, 
                                              {'helper':helper}, 
                                              doc = rpcspec['doc'])

    def __dir__(self):
        ''' Allow tab completion on function names in ipython, and
        other sorts of introspection.  '''
        self._refresh_schema()
        return [i["name"] for i in self._find_in_schema(cls = self._view_or_query)]

    def __repr__(self):
        ''' Pretty representation of the object. '''
        if self._baseurl:
            return self._view_or_query+" object host: ["+self._baseurl+"]"
        else:
            return self._view_or_query+"/local"

class transform_embed(object):
    '''
    Defines a DSL for restricting permissions to analytics and for
    locking down specific parameters. 

    TODO: This is prototype-grade code. It needs a cleanup pass. 
    '''
    def __init__(self, transform_policy, context, embed):
        self._embed = embed
        self._context = context
        self._transform_policy = transform_policy
    
    def _transform(self, function, stripped_args):
        def new_helper(**kwargs):
            args = kwargs
            for arg in stripped_args:
                args[arg] = context[arg]
            return function(**args)
        ## TODO: Use common logic with 
        args = [a for a in inspect.getargspec(function).args if a not in stripped_args]
        if args:
            def_params = ",".join(args)
            call_params = ",".join(["{p}={p}".format(p=p) for p in args])
        else:
            def_params = ""
            call_params = ""
        funcspec = "{name}({params})".format(name=function.__name__, 
                                             params=def_params)
        callspec = "return helper({params})".format(params=call_params)

        return decorator.FunctionMaker.create(funcspec, 
                                              callspec, 
                                              {'helper':new_helper},
                                              doc=function.__doc__)
        return new_helper

    def __getattr__(self, attr):
        if attr[0] == '_':
            return

        permission = self._permission(attr)
        if permission == 'allow':
            return self._embed.__getattr__(attr)
        elif permission == 'deny':
            raise AttributeError(attr)
        elif permission:
            return self._transform(self._embed.__getattr__(attr), permission)
        else:
            raise AttributeError(attr)

    def _permission(self, item):
        default = self._transform_policy.get("default", "deny")
        return self._transform_policy['policy'].get(item, default)

    def __dir__(self):
        listing = self._embed.__dir__()
        filtered = []
        for item in listing:
            if self._permission(item) != 'deny':
                filtered.append(item)
        return filtered

    def __repr__(self):
        return "Secure ["+self._transform_policy['name']+"]:"+self._embed.__repr__()

def get_embed(t, config = None):
    if config: 
        embeds = []
        for embed_spec in config:
            print embed_spec
            embeds.append(single_embed(t, **embed_spec))
        return multi_embed(embeds)
    return single_embed(t)
                                
class djobject():
    def __init__(self, baseurl = None, headers = {}):
        self.view = single_embed('view', baseurl = baseurl, headers = headers)
        self.query = single_embed('query', baseurl = baseurl, headers = headers)

if __name__ == "__main__":
    djo = djobject(baseurl = "http://127.0.0.1:8000/")
    if True: # Internal test -- from djanalytics
        print djo.query.djt_event_count()
        print djo.query.djt_user_event_count(user = "bob")
        print djo.query.__dir__()

    if False: # External test -- from edxanalytics
        transform_policy = {'name': 'test',
                            'default' : 'deny', 
                            'policy' : { 'total_user_count' : 'allow', 
                                         'user_count' : 'allow',
                                         'dash' : 'deny', 
                                         'page_count' : ['user'] }
                            }
        
        context = { 'user' : 'bob',
                    'course' : '6.002x' }
        
        secure_view = transform_embed(transform_policy, context, djo.view)
        print secure_view.__dir__()
        print secure_view.page_count(course = '6.002x')
        print inspect.getargspec(secure_view.page_count)
