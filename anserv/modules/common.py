import logging
log=logging.getLogger(__name__)

def query_results(query):
    from django.db import connection
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        desc = [d[0] for d in cursor.description] # Names of table columns
        results = zip(*cursor.fetchall()) # Results for each column
        return dict(zip(desc, results))
    except:
        log.error("Could not execute query {0}".format(query))
        return {}