''' This is a generic interface to djanalytics. It presents views,
etc. as Python objects. 

This is prototype-grade code. 
'''

import requests
import urllib
import json

schema = None

def find_in_schema(cls = None, name = None):
    items = []
    for item in schema: 
        if cls and item['class'] != cls: 
            continue
        if name and item['name'] != name: 
            continue
        items.append(item)
    return items

def http_rpc_helper(baseurl, view_or_query, function, headers = {}):
    if baseurl: 
        baseembedurl = baseurl+view_or_query+"/"

    def rpc_call(**kwargs):
        url = urllib.basejoin(baseembedurl, function)
        if kwargs:
            url = url+"?"+urllib.urlencode(kwargs)
        print url
        response = requests.get(url, headers = headers)
        if response.status_code == 200:
            return response.content
        if response.status_code == 404:
            raise AttributeError(function)
        error = "Error calling {func} {status}".format(func=function, status=response.status_code)
        raise Exception(error)
    rpc_call.__doc__ = find_in_schema(cls = view_or_query, name = function)[0]['doc']
    return rpc_call

def local_call_helper(view_or_query, function):
    import djanalytics.core.views
    def rpc_call(**kwargs):
        return djanalytics.core.views.handle_request(view_or_query, function, **kwargs)
    return rpc_call

class embed():
    def __init__(self, view_or_query, baseurl = None, headers = {}):
        self._baseurl = baseurl
        self._view_or_query = view_or_query
        self._headers = headers
        self._refresh_schema()

    def _refresh_schema(self):
        global schema
        if not schema:
            if self._baseurl:
                url = self._baseurl+"schema"
                schema = json.loads(requests.get(url).content)
            else: 
                import djanalytics.core.views
                schema = djanalytics.core.views.schema_helper()

    def __getattr__(self, attr):
        ## Disallow internal. This is necessary both for analytics,
        ## and for Python. Otherwise, we have all sorts of __setattr__
        ## and similar overwritten
        if attr[0] == '_':
            return
        if self._baseurl:
            helper = http_rpc_helper(self._baseurl, self._view_or_query, attr)
        else:
            helper = local_call_helper(self._view_or_query, attr)

        # Set the docstring
        helper.__doc__ = find_in_schema(cls = self._view_or_query, name = attr)[0]['doc']
        helper.__name__ = "remote_"+attr
        return helper

    ## TODO: Use probe/schema to populate this
    def __dir__(self):
        self._refresh_schema()
        return [i["name"] for i in find_in_schema(cls = self._view_or_query)]

    def __repr__(self):
        return self._view_or_query+" object host: ["+self._baseurl+"]"
                                
class djobject():
    def __init__(self, baseurl = None, headers = {}):
        self.view = embed('view', baseurl = baseurl, headers = headers)
        self.query = embed('query', baseurl = baseurl, headers = headers)

if __name__ == "__main__":
    djo = djobject(baseurl = "http://127.0.0.1:8000/")
    print djo.query.djt_event_count()
    print djo.query.djt_user_event_count(user = "bob")
    print djo.query.__dir__()
