from distutils.core import setup
from setuptools import find_packages

setup(name='djanalytics', 
      version='0.0',
      package_dir={'djanalytics':'src', 
        'djanalytics.djanalytics' : 'src/djanalytics'}, 
      packages=['djanalytics', 'djanalytics.djanalytics'],
      author="Piotr Mitros, Vik Paruchuri", 
      license="AGPLv3, see LICENSE.txt")
