import nmrglue as ng
from nmrpro.classes.NMRSpectrum import NMRSpectrum, NMRSpectrum2D, DataUdic
from nmrpro.decorators import ndarray_subclasser, perSpectrum
from nmrpro.decorators import *
from nmrglue.process.proc_base import zf_size

@jsCommand(['Processing', 'Zero Filling', 'Zero fill to double size'], [1], args=None)
@jsCommand(['Processing', 'Zero Filling', 'Custom size zero filling'], [1])
@interaction(size={
    '1K': 1024, '2K': 2048, '4K': 4096, '8K': 8192,
    '16K':16384, '32K':32768, '64K':65536, '128K':131074
})
@perSpectrum
@forder(before=['FFT'])
def zf1d(s, size='auto'):
    
    dim = s.udic['ndim'] - 1
    if size == 'auto':
        size = s.udic[dim]['size'] * 2
    ret = ndarray_subclasser(zf_size)(s, size)
    ret.udic[dim]['size'] = size
    return ret

@jsCommand(['Processing', 'Zero Filling', 'Zero fill to double size (2D)'], [2], args=None)
@interaction(size={
    '1K': 1024, '2K': 2048, '4K': 4096, '8K': 8192,
    '16K':16384, '32K':32768, '64K':65536, '128K':131074
}, size2={
    '1K': 1024, '2K': 2048, '4K': 4096, '8K': 8192,
    '16K':16384, '32K':32768, '64K':65536, '128K':131074
})
@perSpectrum
@forder(before=['FFT'])
def zf2d(s, size='auto', size2='auto'):
    ret = zf1d(s, size).tp(copy=False, flag='nohyper')
    ret = zf1d(ret, size2).tp(copy=False, flag='nohyper')
    return ret
