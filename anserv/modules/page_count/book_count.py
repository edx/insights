from modules.decorators import view, query, event_handler
from an_evt.models import StudentBookAccesses

@view('user', 'page_count')
def book_page_count_view(collection, user, params):
    return "The user " + user + " saw "+str(book_page_count_query(collection, user, params))+" pages!"

@query('user', 'page_count')
def book_page_count_query(collection, user, params):
    sba = list(collection.find({'user':user}))
    if len(sba) == 0:
        return 0
    else:
        return sba[0]['pages']
    # sba = StudentBookAccesses.objects.filter(username = user)
    # if len(sba):
    #     pages = sba[0].count
    # else: 
    #     pages = 0
    return pages

@event_handler(queued = False)
def book_page_count_event(collection, response):
    user = response["username"]
    sba = list(collection.find({'user':user}))
    print "XXXX", user, sba
    if len(sba):
        collection.update({'user':user}, {'$inc':{'pages':1}}, True);
    else: 
        collection.insert({'user':user,'pages':1})
    #if len(sba) == 0:
    #    collection.insert({'user':user,'pages':1})
    #else:
    #    collection.
    # sba = StudentBookAccesses.objects.filter(username = response["username"])
    # if len(sba) == 0:
    #     sba = StudentBookAccesses()
    #     sba.username = response["username"]
    #     sba.count = 0
    # else:
    #     sba=sba[0]
    # sba.count = sba.count + 1
    # sba.save()
#    pass
