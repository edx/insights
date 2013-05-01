from distutils.core import setup
from setuptools import find_packages

setup(name = 'djanalytics', 
      version = '0.0',
      package_dir = {'djanalytics':'src/djanalytics'}, 
      packages = ['djanalytics', 'djanalytics.core', 'djanalytics.modulefs', 'djanalytics.modules', 'djanalytics.modules.testmodule'],
      author="Piotr Mitros, Vik Paruchuri", 
      data_files = [("djanalytics/modules/testmodule/static/", ["src/djanalytics/modules/testmodule/static/hello.html"]), 
                    ("djanalytics/modules/testmodule/templates/", ["src/djanalytics/modules/testmodule/templates/hello.html"])],
      license = "AGPLv3, see LICENSE.txt")
