Overview
========
The purpose of this module is to unit test periodic tasks
created with edinsights.core.decorators.cron

The module does not provide any additional functionallity

Despite the name of the module, your periodic tasks
do NOT have to be inside this module. They can be
located in any tasks.py file in any django app
directory.

Running Tests
=============
Because testing periodic tasks is slow (~20s) they
are excluded from testing by default. 

To test the module, add it to INSTALLED_APPS in settings.py

To run the tests: 

    python manage.py test periodic

