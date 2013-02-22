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

def render_query_as_table(query_data):
    html_string="<table><tr><td>Course ID</td><td>Count</td></tr>"
    for i in xrange(0,len(query_data['course_id'])):
        html_string+="<tr><td>{0}</td><td>{1}</td></tr>".format(query_data['course_id'][i],query_data['count'][i])
    html_string+="</table>"
    return html_string
