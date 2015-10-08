from ...classes.NMRSpectrum import NMRSpectrum, DataUdic
from ...decorators import ndarray_subclasser, both_dimensions, perSpectrum
from warnings import warn
import nmrglue.process.proc_base as p

__all__ = ['fft', 'fft_positive', 'fft_norm']

def fft1d(f):
    def fn(s):
        dim = s.udic['ndim'] - 1 
        if s.udic[dim]['freq'] or not s.udic[dim]['time']:
            warn('Input spectrum is in the frequency domain. No FFT is performed.')
            return s
        ffted = f(s)
        ffted.udic[dim]['freq'] = True
        ffted.udic[dim]['time'] = False
        return ffted
    return fn

@perSpectrum
@both_dimensions
def fft(s):
    return fft1d( ndarray_subclasser( p.fft ) )(s)

@perSpectrum
@both_dimensions
def fft_positive(s):
    return fft1d( ndarray_subclasser( p.fft_positive ) )(s)

@perSpectrum
@both_dimensions
def fft_norm(s):
    return fft1d( ndarray_subclasser( p.fft_norm ) )(s)


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
    # Check if the original is complex!!
    fn = lambda s: args_to_function(s, args)
    ret = nmrSpec.fapplyAt(fn, "FFT", "FFT")
    return ret

