import nmrglue as ng
from ...classes.NMRSpectrum import NMRSpectrum, NMRSpectrum2D, DataUdic
from ...decorators import inputs, ndarray_subclasser, perSpectrum

from nmrglue.process.proc_base import zf_size

NEWSPEC, NEWSLIDE, OVERWRITE = 0,1,2


def zf1d(s, size='auto'):
    dim = s.udic['ndim'] - 1
    if size == 'auto':
        size = s.udic[dim]['size'] * 2
    ret = ndarray_subclasser(zf_size)(s, size)
    ret.udic[dim]['size'] = size
    return ret

def zf2d(s, size='auto', size2='auto'):
    ret = zf1d(s, size).tp(copy=False, flag='nohyper')
    ret = zf1d(ret, size2).tp(copy=False, flag='nohyper')
    return ret

@perSpectrum
def ZF(nmrSpec, args):
    two_d = isinstance(nmrSpec, NMRSpectrum2D)
    size = args.get('size', 'auto')
    if two_d:
        size2 = args.get('size2', size)
    
    if not two_d:
        fn = lambda s: zf1d(s, size)
    else:
        fn = lambda s: zf2d(s, size, size2)
    
    out = args.get('out', OVERWRITE)    
    if out in (NEWSPEC, NEWSLIDE):
        return fn(nmrSpec)
    elif out == OVERWRITE:
        if "ZF" in nmrSpec.history.keys():
            return nmrSpec.fapplyAt(fn, "ZF", "ZF")
        
        elif "FFT" not in nmrSpec.history.keys():
            return nmrSpec.fapply(fn, "ZF")
        else:
            return nmrSpec.fapplyBefore(fn, "ZF", "FFT")