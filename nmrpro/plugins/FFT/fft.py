from nmrpro.classes.NMRSpectrum import NMRSpectrum, DataUdic
from nmrpro.decorators import ndarray_subclasser, perDimension, perSpectrum, jsCommand, interaction
from nmrpro.plugins.JSinput2 import Include
from warnings import warn
import nmrglue.process.proc_base as p
import numpy as np

__all__ = ['fft', 'fft_positive', 'fft_norm', 'fft1d']


@perSpectrum
@perDimension
def fft(s):
    ret =  ndarray_subclasser( p.fft )(s)
    _update_udic(ret)
    return ret


@perSpectrum
@perDimension
def fft_positive(s):
    ret = ndarray_subclasser( p.fft_positive )(s)
    _update_udic(ret)
    return ret

@perSpectrum
@perDimension
def fft_norm(s):
    ret = ndarray_subclasser( p.fft_norm )(s)
    _update_udic(ret)
    return ret

@jsCommand(['Processing', 'FFT'], [1,2], args=None)
#@jsCommand(['Processing', 'Advanced FFT'], [1,2])
@interaction(method={'Positive':Include(fft_positive), 'Normalized':Include(fft_norm), 'Default':'fft'}, 
    arglabels={'method':'FFT method'}
)
@perSpectrum
@perDimension
def fft1d(s, method='pos'):
    if not _has_time_domain(s):
        warn('Input spectrum is in the frequency domain. No FFT is performed.')
        return s
    
    if callable(method):
        return method(s)
    
    fn = {
        'fft': fft,
        'norm': fft_norm,
        'pos': fft_positive,
    }[method]
    
    return fn(s)

def _update_udic(s):
    dim = s.udic['ndim'] - 1 
    s.udic[dim]['freq'] = True
    s.udic[dim]['time'] = False

def _has_time_domain(s):
    dim = s.udic['ndim'] - 1 
    if isinstance(s, NMRSpectrum):
        udic = s.original.udic
    else:
        udic = s.udic
    if udic[dim]['freq'] or not udic[dim]['time']:
        return False
    
    return True
    