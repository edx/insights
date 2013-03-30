''' Basic module for test suite. 

Count number of events that hit the server. 
'''

modules_to_import = []

from core.decorators import query, event_handler

@query()
def event_count(db):
    collection = db['event_count']
    t = list(collection.find())
    if len(t):
        return t[0]['event_count']
    return 0

@query()
def user_event_count(db, user):
    collection = db['user_event_count']
    t = list(collection.find({'user':user}))
    if len(t):
        return t[0]['event_count']
    return 0

@query()
def clear_database(db):
    collection = db['event_count']
    collection.remove({})
    collection = db['user_event_count']
    collection.remove({})
    return "Database clear"

@event_handler()
def event(db, events):
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
def event(fs, events):
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
    if fs.exists(filename): 
        f=fs.open(filename)
        return f.read()
    return "File not found"
