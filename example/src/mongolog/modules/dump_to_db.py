import sys

from djanalytics.core.decorators import event_handler

@event_handler()
def dump_to_db(db, events):
    ## TODO: Error handling
    collection = db['event_log']
    collection.insert([e.event for e in events])

