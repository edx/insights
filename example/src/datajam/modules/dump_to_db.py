from edinsights.core.decorators import event_handler


@event_handler()
def dump_to_db(mongodb, events):
    ## TODO: Error handling
    collection = mongodb['event_log']
    collection.insert([e.event for e in events])
