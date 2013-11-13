from distutils.core import setup
from setuptools import find_packages

setup(
    name = 'edinsights', 
    version = '0.1',
    description='edX Insights Analytics Framework',
    package_dir = {'edinsights':'src/edinsights'}, 
    packages = ['edinsights', 'edinsights.core', 'edinsights.modulefs', 'edinsights.modules', 'edinsights.modules.testmodule'],
    author="Piotr Mitros, Vik Paruchuri", 
    data_files = [
        ("edinsights/modules/testmodule/static/", ["src/edinsights/modules/testmodule/static/hello.html"]), 
        ("edinsights/modules/testmodule/templates/", ["src/edinsights/modules/testmodule/templates/hello.html"])
    ],
    license = "AGPLv3, see LICENSE.txt"
)
