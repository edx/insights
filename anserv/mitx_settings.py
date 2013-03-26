import sys
import os

from path import path

XQUEUE_INTERFACE = {
    "url": "http://127.0.0.1:3032",
    "django_auth": {
        "username": "lms",
        "password": "abcd"
    },
    "basic_auth": ('anant', 'agarwal'),
    }

MITX_FEATURES = {
    'SAMPLE': False,
    'USE_DJANGO_PIPELINE': True,
    'DISPLAY_HISTOGRAMS_TO_STAFF': True,
    'REROUTE_ACTIVATION_EMAIL': False,		# nonempty string = address for all activation emails
    'DEBUG_LEVEL': 0,				# 0 = lowest level, least verbose, 255 = max level, most verbose

    ## DO NOT SET TO True IN THIS FILE
    ## Doing so will cause all courses to be released on production
    'DISABLE_START_DATES': False,  # When True, all courses will be active, regardless of start date

    # When True, will only publicly list courses by the subdomain. Expects you
    # to define COURSE_LISTINGS, a dictionary mapping subdomains to lists of
    # course_ids (see dev_int.py for an example)
    'SUBDOMAIN_COURSE_LISTINGS': False,

    # When True, will override certain branding with university specific values
    # Expects a SUBDOMAIN_BRANDING dictionary that maps the subdomain to the
    # university to use for branding purposes
    'SUBDOMAIN_BRANDING': False,

    'FORCE_UNIVERSITY_DOMAIN': False,  	# set this to the university domain to use, as an override to HTTP_HOST
    # set to None to do no university selection

    'ENABLE_TEXTBOOK': True,
    'ENABLE_DISCUSSION_SERVICE': True,

    'ENABLE_PSYCHOMETRICS': False,  	# real-time psychometrics (eg item response theory analysis in instructor dashboard)

    'ENABLE_SQL_TRACKING_LOGS': False,
    'ENABLE_LMS_MIGRATION': False,
    'ENABLE_MANUAL_GIT_RELOAD': False,

    'DISABLE_LOGIN_BUTTON': False,  # used in systems where login is automatic, eg MIT SSL

    'STUB_VIDEO_FOR_TESTING': False,   # do not display video when running automated acceptance tests

    # extrernal access methods
    'ACCESS_REQUIRE_STAFF_FOR_COURSE': False,
    'AUTH_USE_OPENID': False,
    'AUTH_USE_MIT_CERTIFICATES': False,
    'AUTH_USE_OPENID_PROVIDER': False,

    # analytics experiments
    'ENABLE_INSTRUCTOR_ANALYTICS': False,

    # Flip to True when the YouTube iframe API breaks (again)
    'USE_YOUTUBE_OBJECT_API': False,

    # Give a UI to show a student's submission history in a problem by the
    # Staff Debug tool.
    'ENABLE_STUDENT_HISTORY_VIEW': True
}

############################# SET PATH INFORMATION #############################
REPO_ROOT = path(__file__).abspath().dirname().dirname()  # /mitx/lms
ENV_ROOT = REPO_ROOT.dirname()  # virtualenv dir /mitx is in
COURSES_ROOT = ENV_ROOT / "data"

DATA_DIR = COURSES_ROOT

MODULESTORE = {
    'default': {
        'ENGINE': 'xmodule.modulestore.xml.XMLModuleStore',
        'OPTIONS': {
            'data_dir': DATA_DIR,
            'default_class': 'xmodule.hidden_module.HiddenDescriptor',
            }
    }
}

GENERATE_PROFILE_SCORES = False


