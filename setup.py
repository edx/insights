from distutils.core import setup
from setuptools import find_packages

setup(
    name = 'edinsights', 
    version = '0.1',
    description='edX Insights Analytics Framework',
    package_dir = {'edinsights':'src/edinsights'}, 
    packages = ['edinsights', 'edinsights.core', 'edinsights.modulefs', 'edinsights.modules'],
    author="Piotr Mitros, Vik Paruchuri", 
    license = "AGPLv3, see LICENSE.txt"
)
