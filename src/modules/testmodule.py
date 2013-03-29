''' Basic module for test suite. 

Count number of events that hit the server. 
'''

modules_to_import = []

from djanalytics.decorators import query, event_handler

@query()
def event_count(db):
    collection = db['event_count']
    t = list(collection.find())
    if len(t):
        return t[0]['event_count']
    return 0

@query()
def clear_database(db):
    collection = db['event_count']
    collection.remove({})
    return "Database clear"

@event_handler()
def event(fs, db, events):
    for resp in events:
        collection = db['event_count']
        t = list(collection.find())
        if len(t): 
            collection.update({}, {'$inc':{'event_count':1}})
        else:
            collection.insert({'event_count' : 1})
    return 0
