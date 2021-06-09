from distutils.core import setup
from os.path import exists
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

setup(
  name = 'nmrpro',
  packages = find_packages(), # this must be the same as the name above
  version = '0.2.8',
  description = 'Interactive processing of NMR Spectra',
  author = 'Ahmed Mohamed',
  author_email = 'mohamed@kuicr.kyoto-u.ac.jp',
  install_requires=['numpy', 'scipy', 'nmrglue>=0.5'],
  dependency_links=['https://github.com/jjhelmus/nmrglue/archive/master.zip#egg=nmrglue-0.6'],
  url = 'https://github.com/ahmohamed/nmrpro', # use the URL to the github repo
  license='MIT',
  keywords = ['nmr', 'spectra', 'multi-dimensional'],
  classifiers = [],
)