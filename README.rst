NMRPRo python package
=====================

This package reads and processes different types of NMR spectra. 
NMRPro python package consists of two main parts: 

Core 
****

The core provides 4 different classes for representing NMR spectra. All spectra regarless of their original format are stored as NMRSpectrum object, which frees the user from dealing with format-specific processing. Also, it encapsulates multi-dimesional processing for 2D spectra, by applying the processing functions to each dimension.

Plugins
*******

Plugins provide functions necessary for automatic spectral processing, and allow for easy extensibility of the package. Currently implemented plugins are Zero-filling, Apodization, FT, Phase correction (automatic), Baseline correction and Peak picking.


