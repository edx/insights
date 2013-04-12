This is a minimal application built on top of djanalytics. 

All it does is stream events verbatim into a database. 

To run this, first install djanalytics: 

    sudo python setup.py install

Do the same for: 

    https://github.com/edx/loghandlersplus
    https://github.com/edx/djeventstream

Now, 

    cd example/src/mongolog/
    python manage.py syncdb
    python manage.py migrate
    python manage.py runserver localhost:8020

The server should be running. To stream an event, run: 

    cd example/src/sendevent

To confirm the event is there: 

    mongo
    show dbs
    use modules_dump_to_db
    show collections
    db.getCollection("event_log").find()

This is test and working as of April 12, 2013. This is not a normal
test case, so please let me know if this breaks (it is not entirely
unexpected that it might; the API is still quite fluid as of April).
