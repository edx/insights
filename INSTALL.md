
In order to install the minimal analytics-experiments repository:

First, decide on your directories:
* VIRTUALENV_DIR = directory where you create your python virtualenv.
* BASE_DIR = directory you start in before cloning the analytics repo. (so something like /home/bob)
* ANALYTICS_DIR = directory where the analytics-experiments repo is cloned. (so something like /home/bob/analytics-experiments/)

Then, start to install:
* cd BASE_DIR
* git clone git@github.com:MITx/analytics-experiments.git
* cd analytics-experiments (this is the ANALYTICS_DIR)
* sudo xargs -a apt-packages.txt apt-get install
* sudo aptitude remove python-virtualenv python-pip
* sudo easy_install pip virtualenv
* pip install virtualenv
* mkdir VIRTUALENV_DIR
* virtualenv VIRTUALENV_DIR
* source VIRTUALENV_DIR/bin/activate
* cd ANALYTICS_DIR
* pip install -r requirements.txt
* mkdir BASE_DIR/db
* cd ANALYTICS_DIR/anserv
* Ensure that IMPORT_MITX_MODULES in settings.py is False .
* python manage.py syncdb --database=default --settings=settings (this may fail, but that is fine)
* python manage.py syncdb --database=local --settings=settings
* mkdir ANALYTICS_DIR/staticfiles
* python manage.py collectstatic --settings=settings --noinput -c --pythonpath=.

Then, run the server:
* python manage.py runserver 127.0.0.1:9022 --settings=settings --pythonpath=. --nostatic
* Navigate to 127.0.0.1:9022 in your browser, and you should see a login screen.

Then, create a user:
* cd ANALYTICS_DIR/anserv
* python manage.py shell --settings=settings
* from django.contrib.auth.models import User (run in the shell)
* user = User.objects.create_user("test","test@test.com","test") (run in the shell)

If you are using the aws settings (ie deploying):

* MITX_DIR = directory where you clone MITX

* cd ANALYTICS_DIR/anserv
* source VIRTUALENV_DIR/bin/activate
* python manage.py createcachetable django_cache --database=local
* cd BASE_DIR
* git clone git@github.com:MITx/mitx.git
* cd MITX_DIR
* sudo xargs -a apt-packages.txt apt-get install
* pip install -r pre-requirements.txt



