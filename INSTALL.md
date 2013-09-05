Prior to installing, install djeventstream and loghandlersplus:

    https://github.com/edx/djeventstream
    https://github.com/edx/loghandlersplus

To install a development setup: 

    sudo apt-get install python-pip python-matplotlib python-scipy emacs mongodb apache2-utils python-mysqldb subversion ipython nginx git redis-server
    git clone https://github.com/edx/insights
    cd insights
    pip install -r requirements.txt    
    cd src/edinsights/
    python manage.py syncdb
    python manage.py migrate
    python manage.py runserver localhost:9022

To install a setup to build from: 

    sudo apt-get install python-pip python-matplotlib python-scipy emacs mongodb apache2-utils python-mysqldb subversion ipython nginx git redis-server
    git clone https://github.com/edx/insights
    cd insights
    pip install -r requirements.txt    
    sudo python setup.py install
