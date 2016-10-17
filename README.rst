.. image:: https://travis-ci.org/ahmohamed/nmrpro.svg?branch=release
    :target: https://travis-ci.org/ahmohamed/nmrpro

NMRPRo python package
=====================

TL;DR
*****

NMRPro reads and processes different types of NMR spectra. This package is released as part of an integrated web component 
`NMRPro <http://mamitsukalab.org/tools/nmrpro/>`_. The package can also be used directly from python. Refer to the 
`tutorial </tutorial/NMRPro_tutorial.ipynb>`_ for examples.

Installation
************

NMRPro can be installed directly from *pypi*::

  pip install nmrpro



Getting started
***************

As a web component
------------------

NMRPro package is written as part of an integrated web component. When installed with the companion `Django App <https://github.com/ahmohamed/django_nmrpro>`_, it can be used to process NMR spectra online interactively. Please refer to the `Web component home page <http://mamitsukalab.org/tools/nmrpro/>`_ for installation instructions.

Standalone
----------
NMRPro package is written also to eanble using it from python directly. NMRPro is a high level wrapper for `nmrglue package <https://github.com/jjhelmus/nmrglue/>`_. It provides several functions to facilitate dealing with NMR spectra.


Please have a look at `the tutorial <https://github.com/ahmohamed/nmrpro/blob/master/tutorial/NMRPro_tutorial.ipynb>`_ to get started.

Extending NMRPro
****************

Experienced users can extend the package by writing plugin functions (Both Python and R are supported now). Writing plugins requires no extra knowledge of NMRPro object structure or familiarity with web technologies. Plugins are autoamtically integrated with the rest of the web component with no extra code.

Please refer to the following tutorials for more information.

1. `Basic plugin development <https://github.com/ahmohamed/nmrpro/blob/master/tutorial/For_developers.ipynb>`_: An overview of the basic plugin architure illustrated by examples.
2. `Advanced development <https://github.com/ahmohamed/nmrpro/blob/master/tutorial/Advanced_tutorial.ipynb>`_: Special cases for plugin development, such as cutomizing the web GUI, combining multiple functions into a single command and working with R functions. 


Support
*******
Please contact me if you face any installtion problems, or discover any bugs (mohamed .at. kuicr.kyoto-u.ac.jp).

More Details?
*************

NMRPro package structure
************************

NMRPro python package consists of two main parts: 

Core
----

The core provides 4 different classes for representing NMR spectra. All spectra regarless of their original format are stored as NMRSpectrum object, which frees the user from dealing with format-specific processing. Also, it encapsulates multi-dimesional processing for 2D spectra, by applying the processing functions to each dimension.

Plugins
-------

Plugins provide functions necessary for automatic spectral processing, and allow for easy extensibility of the package. Currently implemented plugins are Zero-filling, Apodization, FT, Phase correction (automatic), Baseline correction and Peak picking.


