Prior to installing, install djeventstream:

    https://github.com/edx/djeventstream

To install a development setup: 

    cat apt-packages.txt | xargs sudo apt-get -yq install
    git clone https://github.com/edx/insights
    cd insights
    pip install -r requirements.txt    
    cd src
    python manage.py syncdb
    python manage.py migrate
    python manage.py runserver localhost:9022

To install a setup to build from: 

    cat apt-packages.txt | xargs sudo apt-get -yq install
    git clone https://github.com/edx/insights
    cd insights
    pip install -r requirements.txt    
    sudo python setup.py install
