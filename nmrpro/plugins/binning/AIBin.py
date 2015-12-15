from ...classes.NMRSpectrum import NMRDataset
from nmrpro.exceptions import NMRTypeError, ArgumentError
import numbers
import numpy as np

__all__ = ['AIBin']

def AIBin(dataset, minbinsize='0.4ppm', noise_regions='last_10%', R=0.5):
    '''
    Find optimal bin boundaries using Adaptive Intelligent binning algorithm.
    
    The algorithm is desbribed in detail in:
    De Meyer, Tim, et al. Analytical Chemistry 80.10 (2008): 3783-3790.
    
    Note: Because of the iterative nature of the algorithm, it may take upto to an hour
    on 64k points spectra.
    '''
    # check args
    if not isinstance(dataset, list):
        if isinstance(dataset, NMRDataset):
            data = dataset.specList
        else:
            raise NMRTypeError('AI binning accepts 1D datasets only')
    else: data = dataset
    
    if isinstance(minbinsize, basestring):
        try: minbinsize = abs(data[0].interval(minbinsize))
        except ValueError:
            raise ArgumentError('Incompatible argument, minbinsize: %s' %minbinsize)
    
    if not isinstance(minbinsize, numbers.Number):
        raise ArgumentError('Incompatible argument, minbinsize: %s' %minbinsize)
    
    data = np.array(data)
    if noise_regions == 'last_10%':
        size = data.shape[-1]
        noise_regions = ((0, int(size * 0.1)),)
    
    Vnoise = max([getVnoise(data[:, r[0]:r[1]], R) for r in noise_regions])
    bins = optimize_boundry(data, Vnoise=Vnoise, R=R, minbinsize=minbinsize)
    return bins

def VbScore(arr, b=None, R=0.5):
    '''
    Calculates the Vb scores according to the formula given in the paper.
    
    .. math::
        V_b = \frac{1}{S} \sum_{j=1}^{s} (max_j - I_{j,1}) * (max_j - I_{j,end})^R
    '''
    if b is None:
        b = (0,arr.shape[-1] -1)
    start, end = b
    max_ = np.max(arr[:,start:end], axis=-1).astype(np.float64)
    scores = (max_ - arr[:,start])*(max_ - arr[:,end])
    if np.any(scores < 0):
        return 0.
    
    scores = scores**R
    return np.mean(scores)

def optimize_boundry(arr, b=None, Vb=0, Vnoise=0, R=0.5, minbinsize=1):
    '''
    Searches for optimal bin boundary in the given dataset.
    
    The function tests every point in the array to maximize Vb. The array is then
    divided at the boundary and the the function is called recursively until no
    divisions are possible.    
    '''
    if b is None: #First bin is the whole array
        b = tuple((0, arr.shape[-1] - 1))
        Vb = VbScore(arr, b, R)
    
    if minbinsize < 1: minbinsize = 1
    
    R = 0.5
    max_stride = 0
    Vb_max = Vb1_max = Vb2_max = 0
    bstart, bend = b
    
    for i in range(bstart + minbinsize, bend - minbinsize): #where b is parent bin
        b1 = tuple((bstart, i))
        b2 = tuple((i+1, bend))
        Vb1, Vb2 = [VbScore(arr, b1, R), VbScore(arr, b2, R)] # Vb1, Vb2

        if (Vb1 + Vb2) > Vb_max:
            Vb_max = Vb1 + Vb2
            Vb1_max = Vb1
            Vb2_max = Vb2
            max_stride = i

    if Vb_max > Vb and Vb1_max > Vnoise and Vb2_max > Vnoise:
        # B1, B2 are new bins
        B1 = tuple((bstart, max_stride))
        B2 = tuple((max_stride+1, bend))
        B1 = optimize_boundry(arr, b=B1, Vb=Vb1_max, Vnoise=Vnoise, R=R)
        B2 = optimize_boundry(arr, b=B2, Vb=Vb2_max, Vnoise=Vnoise, R=R)
        return (B1 + B2)
    else:
        return (b,)

def getVnoise(arr, R=0.5):
    '''Calculates the Vbmax for noise region'''
    noise_bins = optimize_boundry(arr, R=R)
    Vbs = [VbScore(arr, b, R) for b in noise_bins]
    return max(Vbs)
