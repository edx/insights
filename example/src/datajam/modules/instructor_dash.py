import json

from edinsights.core.decorators import query

@query()
def analytics_get(aname, course_id, apikey):
    '''
    Dummy analytics for the analytics tab on the LMS instructor dashboard.
    '''

    # return a timestamp indicating when the data was calculated
    retval = {'time': 'fabricated today'}

    if aname == "StudentsEnrolled":
        # num students enrolled
        retval['data'] = [{'students': '3000'}]

    elif aname == "StudentsActive":
        # num students active in time period (default = 1wk)
        retval['data'] = [{'active': '300'}]
    
    elif aname == "StudentsDropoffPerDay":
        # active students dropoff by day
        retval['data'] = [
                {'last_day': '20131027T0910', 'num_students': '700'},
                {'last_day': '20131028T0910', 'num_students': '500'},
                {'last_day': '20131029T0910', 'num_students': '300'},
                {'last_day': '20131030T0910', 'num_students': '200'},
        ]
    
    elif aname == "ProblemGradeDistribution":
        # foreach problem, grade distribution
        retval['data'] = [
            {
                'module_id': 'blah/blah/module1',
                'grade_info': [
                    {'max_grade': '10', 'grade': '10', 'num_students': '10'},
                    {'max_grade': '20', 'grade': '20', 'num_students': '12'},
                    {'max_grade': '30', 'grade': '30', 'num_students': '11'},
                ],
            },
            {
                'module_id': 'blah/blah/module2',
                'grade_info': [
                    {'max_grade': '10', 'grade': '10', 'num_students': '8'},
                    {'max_grade': '20', 'grade': '20', 'num_students': '11'},
                    {'max_grade': '30', 'grade': '30', 'num_students': '15'},
                ],
            },
        ]

    # These are not currently displayed by the analytics dash:
    # if aname == "OverallGradeDistribution",  # overall point distribution for course
    # if aname == "StudentsPerProblemCorrect",  # foreach problem, num students correct
    # if aname == "StudentsAttemptedProblems",  # num students who tried given problem
    # elif aname == "StudentsDailyActivity":  # active students by day
    
    return json.dumps(retval)
