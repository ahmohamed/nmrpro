from distutils.core import setup

setup(
  name = 'nmrpro',
  packages = ['nmrpro'], # this must be the same as the name above
  version = '0.1',
  description = 'A processing library for processing NMR Spectra',
  author = 'Ahmed Mohamed',
  author_email = 'mohamed@kuicr.kyoto-u.ac.jp',
  requires=['numpy', 'scipy', 'nmrglue'],
  url = 'https://github.com/ahmohamed/nmrpro', # use the URL to the github repo
  download_url = 'https://github.com/ahmohamed/nmrpro/tarball/0.1', # I'll explain this in a second
  keywords = ['nmr', 'spectra', 'multi-dimensional'],
  classifiers = [],
)