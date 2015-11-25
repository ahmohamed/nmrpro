from ...classes.NMRSpectrum import NMRSpectrum, DataUdic
from ...decorators import ndarray_subclasser, both_dimensions, perSpectrum
from warnings import warn
import nmrglue.process.proc_base as p

__all__ = ['fft', 'fft_positive', 'fft_norm', 'fft1d']

@perSpectrum
@both_dimensions
def fft1d(s, method='pos'):
    if not _has_time_domain(s):
        warn('Input spectrum is in the frequency domain. No FFT is performed.')
        return s
    
    fn = {
        'fft': fft,
        'norm': fft_norm,
        'pos': fft_positive,
    }[method]
    
    return fn(s)
    
@perSpectrum
@both_dimensions
def fft(s):
    ret =  ndarray_subclasser( p.fft )(s)
    _update_udic(ret)
    return ret

@perSpectrum
@both_dimensions
def fft_positive(s):
    ret = ndarray_subclasser( p.fft_positive )(s)
    _update_udic(ret)
    return ret

@perSpectrum
@both_dimensions
def fft_norm(s):
    ret = ndarray_subclasser( p.fft_norm )(s)
    _update_udic(ret)
    return ret


@both_dimensions
def args_to_function(spec, args):
    algorithm = args.get('a','pos')
    fn = {
        'fft': fft,
        'norm': fft_norm,
        'pos': fft_positive,
    }[algorithm]
    return fn(spec)

@perSpectrum
def webFFT(nmrSpec, args):
    # # Check if the original is complex!!
    # fn = lambda s: args_to_function(s, args)
    # ret = nmrSpec.fapplyAt(fn, "FFT", "FFT")
    return fft1d(nmrSpec, args.get('a','pos'))


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
    