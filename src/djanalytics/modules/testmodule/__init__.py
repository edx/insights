''' Basic module containing events, views, and queries for the test suite. 

'''

modules_to_import = []

from djanalytics.core.decorators import query, event_handler, view, event_property

@view()
def hello_template():
    from djanalytics.core.render import render
    return render("hello.html", {})

@query()
def event_count(db):
    ''' Number of hits to event_handler since clear_database
    '''
    collection = db['event_count']
    t = list(collection.find())
    if len(t):
        return t[0]['event_count']
    return 0

@query()
def user_event_count(db, user):
    ''' Number of hits by a specific user to event_handler since
    clear_database
    '''
    collection = db['user_event_count']
    t = list(collection.find({'user':user}))
    if len(t):
        return t[0]['event_count']
    return 0

@query()
def clear_database(db):
    ''' Clear event counts
    '''
    collection = db['event_count']
    collection.remove({})
    collection = db['user_event_count']
    collection.remove({})
    return "Database clear"

@event_handler()
def event_count_event(db, events):
    ''' Count events per user and per system. Used as test case for
    per-user and global queries. '''
    for evt in events:
        if 'user' in evt:
            collection = db['user_event_count']
            user = evt['user']
            t = list(collection.find({'user' : user}))
            if len(t): 
                collection.update({'user' : user}, {'$inc':{'event_count':1}})
            else:
                collection.insert({'event_count' : 1, 'user' : user})
        collection = db['event_count']
        t = list(collection.find())
        if len(t): 
            collection.update({}, {'$inc':{'event_count':1}})
        else:
            collection.insert({'event_count' : 1})
    return 0

@event_handler()
def python_fs_forgets(fs, events):
    ''' Test case for checking whether the file system properly forgets. 
    To write a file: 

    { 'fs_forgets_contents' : True, 
      'filename' : "foo.txt",
      'contents' : "hello world!"}

    To set or change expiry on a file: 
    { 'fs_forgets_expiry' : -5, 
      'filename' : "foo.txt"}

    The two may be combined into one operation. 
    '''
    def checkfile(filename, contents):
        if not fs.exists(filename):
            return False
        if fs.open(filename).read == contents:
            return True
        raise Exception("File contents do not match")
    for evt in events:
        if 'fs_forgets_contents' in evt:
            f=fs.open(evt['filename'], 'w')
            f.write(evt['fs_forgets_contents'])
            f.close()
        if 'fs_forgets_expiry' in evt:
            try: 
                fs.expire(evt['filename'], evt['fs_forgets_expiry'])
            except:
                print "Failed"
                import traceback
                traceback.print_exc()
    return 0

@event_handler()
def python_fs_event(fs, events):
    ''' Handles events which will create and delete files in the
    filesystem. 
    '''
    for evt in events:
        if 'event' in evt and evt['event'] == 'pyfstest':
            if 'create' in evt:
                f=fs.open(evt['create'], 'w')
                f.write(evt['contents'])
                f.close()
            if 'delete' in evt and fs.exists(evt['delete']): 
                fs.remove(evt['delete'])

@query()
def readfile(fs, filename):
    ''' Return the contents of a file in the fs. 
    '''
    if fs.exists(filename): 
        f=fs.open(filename)
        return f.read()
    return "File not found"

@query()
def cache_get(cache, key):
    result = cache.get(key)
    return result

@event_handler()
def cache_set(cache, events):
    for evt in events:
        if 'event' in evt and evt['event'] == 'cachetest':
            cache.set(evt['key'], evt['value'], evt['timeout'])

@event_property(name="agent")
def agent(event):
    ''' Returns the user that generated the event. The terminology of
    'agent' is borrowed from the Tincan agent/verb/object model. '''
    if "user" in event:
        return event["user"]
    elif "username" in event:
        return event["username"]
    else:
        return None

@event_handler()
def event_property_check(cache, events):
    for evt in events:
        if "event_property_check" in evt:
            cache.set("last_seen_user", evt.agent, 30)

@query()
def fake_user_count():
    return 2

@view()
def fake_user_count(query):
    ''' Test of an abstraction used to call queries, abstracting away
    the network, as well as optional parameters like fs, db, etc. 
    '''
    return "<html>Users: {uc}</html>".format(uc = query.fake_user_count())
