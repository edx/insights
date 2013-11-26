from bson.json_util import dumps

from edinsights.core.decorators import event_handler
from edinsights.core.decorators import query


@query()
def all_problem_answers(mongodb):
    """
    Returns a list of records each containing the problem, the student response
    and the number of times that response has been seen for that problem.

    Example::
    
        [
          { 
            "question": "i4x-edX-E101-problem-a0effb954cca4759994f1ac9e9434bf4_3_1",
            "answer": "choice_0",
            "count": 5
          },
          { 
            "question": "i4x-edX-E101-problem-a0effb954cca4759994f1ac9e9434bf4_3_1",
            "answer": "blue",
            "count": 30
          },
        ]
    """
    return dumps(mongodb['problem_answers'].find())


@event_handler()
def handle_problem_checks(mongodb, events):
    collection = mongodb['problem_answers']
    answers = []
    for event_wrapper in events:
        event = event_wrapper.event
        has_event_field = 'event' in event
        is_problem_check = event.get('event_type') == 'problem_check'
        is_from_server = event.get('event_source') == 'server'
        if is_problem_check and is_from_server and has_event_field:
            for question, answer in event.get('event', {}).get('answers', {}).iteritems():
                collection.update(
                    {
                        'question': question,
                        'answer': answer
                    },
                    { '$inc': {'count': 1} },
                    upsert=True
                )
