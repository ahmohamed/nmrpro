from distutils.core import setup
from os.path import exists
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

setup(
  name = 'nmrpro',
  packages = find_packages(), # this must be the same as the name above
  version = '0.1',
  description = 'Interactive processing of NMR Spectra',
  author = 'Ahmed Mohamed',
  author_email = 'mohamed@kuicr.kyoto-u.ac.jp',
  requires=['numpy', 'scipy', 'nmrglue'],
  url = 'https://github.com/ahmohamed/nmrpro', # use the URL to the github repo
  #download_url = 'https://github.com/ahmohamed/nmrpro/tarball/0.1',
  license='MIT',
  keywords = ['nmr', 'spectra', 'multi-dimensional'],
  classifiers = [],
)