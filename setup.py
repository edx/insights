from distutils.core import setup
from setuptools import find_packages

setup(name='djanalytics', 
      version='0.0',
      package_dir={'djanalytics.an_evt' : 'src/an_evt'}, 
      packages=['djanalytics', 'djanalytics.an_evt'],
      author="Piotr Mitros, Vik Paruchuri", 
      license="AGPLv3, see LICENSE.txt")
