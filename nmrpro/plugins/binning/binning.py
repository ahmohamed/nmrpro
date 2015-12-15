from ...classes.NMRSpectrum import NMRSpectrum, DataUdic
from ...decorators import ndarray_subclasser, both_dimensions, perSpectrum
from warnings import warn
import nmrglue.process.proc_base as p
import numbers
import numpy as np

__all__ = ['bin']

#@dataset
def optimizedBucket(dataset, binsize='0.4ppm', slackness=0.5, reference_method='max'):
    if not isinstance(binsize, numbers.Number):
        binsize = abs(dataset[0].interval(binsize))
    
    if binsize <= 1:
        return s
    
    #Create reference spectrum
    method = {
        'max':np.max,
        'mean':np.mean
    }[reference_method]
    
    ref = method(np.array(dataset.specList), axis=0)
    
    N = ref.shape[-1] -1
    slackness = int(slackness * binsize)
    slices = range(0, N, binsize)
    slices[1:] = [ (s-slackness) + np.argmin(ref[s-slackness:s+slackness]) for s in slices[1:] ]
    slices.append(N)
    return slices

@perSpectrum
@both_dimensions
def binSpectrum(s, binsize='0.4ppm'):
    if not isinstance(binsize, numbers.Number):
        binsize = abs(s.interval(binsize))
    
    if binsize <= 1:
        return s
    
    N = s.shape[-1] -1
    slices = np.arange(0, N, binsize).astype(np.int)
    counts = np.diff(np.append(slices, N)).astype(np.float)
    ret = np.add.reduceat(s, slices) / counts
    ret.udic[ret.udic['ndim']-1]['size'] = ret.shape[-1]
    return ret
    

@perSpectrum
def webBin(nmrSpec, args):
    fn = lambda s: binSpectrum(s, args.get('binsize', '0.4ppm')
    ret = nmrSpec.fapply(fn, "bin")
    return ret

