import numpy as np
from numpy.fft import rfft, irfft
from scipy.stats import nanmean, nanmedian
import numbers

__all__ = ['fft_crosscor', 'crosscor_shift', 'apply_shift', 'icoshift']

def icoshift(target, x_matrix, intervals='whole', perform_coshift=False):
    '''
    interval Correlation Optimized shifting
    
    Splits a spectral database into "inter" intervals and coshift each vector
    left-right to get the maximum correlation toward a reference or toward an
    average spectrum in that interval. Missing parts on the edges after
    shifting are filled with "closest" value.    
    '''
    signal_size = x_matrix.shape[-1]
    intervals = calculate_intervals(intervals, signal_size)
    
    if perform_coshift:
        if target == 'average2':
            # This is a special case. average2 calls icoshift once to
            # calculate the target. Therefore, coshift should be perfomed 
            # before the target is calculated.
            x_matrix = icoshift('average', x_matrix, 'whole')
            target = calculate_target(target, x_matrix, intervals)
        else:
            # Otherwise the coshift should be perform on the same target as icoshift
            target = calculate_target(target, x_matrix, intervals)
            x_matrix = icoshift(target, x_matrix, 'whole')
    else:
        target = calculate_target(target, x_matrix, intervals)
    
    slices = intervals2slices(intervals, signal_size)
    shifted = np.zeros_like(x_matrix)
    for slice_ in slices:
        # loop over slices, get the maximum cross-cor shift and apply it.
        shifts = crosscor_shift(target[slice_], x_matrix[:, slice_], n='f')
        shifted[:, slice_] = apply_shift(x_matrix[slice_], shifts, fill_with_previous=True)
    
    return shifted

def fft_crosscor(target, x_matrix, normalize=True):
    '''
    Computes the cross-correlation between a `target` singal (1D) and 
    multiple 1D signals simulatneously. `x_matrix` is a 2D array where
    each row represent one signal.
    '''
    # Implementation based on scipy.signal.fftconvolve
    size = target.shape[-1] + x_matrix.shape[-1] - 1
    fsize = 2 ** np.ceil(np.log2(size)).astype(int)
    cc = irfft(rfft(target, fsize) *
                rfft(x_matrix, fsize).conjugate()).real
    
    if not normalize:
        return cc
    
    norms = np.linalg.norm(x_matrix, axis=-1) * np.linalg.norm(target)
    cc /= norms.reshape(1,-1).T
    return cc

def crosscor_shift(target, x_matrix, n='f'):
    '''
    Computes the shifts needed in the `x_matrix` rows to maximize the
    cross-correlation with `target`
    '''
    if n == 'f':
        n = x_matrix.shape[-1]
    
    print n
    size = x_matrix.shape[-1]
    cross_cor = fft_crosscor(target.real, x_matrix.real)
    # Get the window, where signals can be shifted (within the maximum shift)
    # Plus 1 compansates for 'no-shift' index (zero)
    window = range(n + 1)
    window.extend(range(cross_cor.shape[-1] - n, cross_cor.shape[-1]))

    # Get the max cross-correlation within the window
    ind = np.argmax(cross_cor[:,window], -1)

    # Maxima at the second half of the window indicate a negative shift.
    ind[ind > n] -= len(window)
    return ind

def apply_shift(x_matrix, shifts, fill_with_previous=True):
    '''Shifts the provided signals by `shifts` points'''
    if len(shifts) != x_matrix.shape[0]:
        raise ValueError('Number of shifts must be equal to number of signals.')
    
    ret = np.zeros_like(x_matrix)
    
    if not fill_with_previous:
        ret = ret.astype(np.float64) # Change the dtype to float to enable storing NaN values.
    
    for i, vec in enumerate(x_matrix):
        n = shifts[i]
        if n == 0:
            ret[i, :] = vec
            continue
        
        
        shifted = np.roll(vec, n)
        
        if fill_with_previous:
            # If the shift is positive, fill with the first element.
            # If the shift is negative, fill with the last element.
            filling = vec[0] if n > 0 else vec[-1]
        else:
            filling = np.nan
            shifted = shifted.astype(np.float64) # Change the dtype to float to enable storing NaN values.
        
        # Replace the shifted region with the filling
        if n > 0: 
            shifted[:n] = filling
        else: # n is negative, the shifted region is the last n-elements of the array.
            shifted[n:] = filling
        
        ret[i, :] = shifted
    
    return ret
    

################ Helper functions for icoshift parameters ################

def calculate_intervals(intervals, size):
    if intervals == 'whole':
        return (0,size)
    
    if isinstance(intervals, numbers.Number):
        intervals = float(intervals)
        slices = np.arange(0, size, np.ceil(size/intervals)).astype(np.int)
        return slices
    
    # Intervals is already a list
    return intervals

def intervals2slices(intervals, size):
    ret = list()
    for i in range(len(intervals)):
        if i == len(intervals) -1: # last element
            if intervals[-1] == size: break
            else:
                ret.append(slice(intervals[-1], size))
        else:
            ret.append(slice(intervals[i], intervals[i+1]))
    
    return ret

def slices2intervals(slices):
    return [s.start for s in slices]

def calculate_target(target, x_matrix, intervals, average_multiplier=3):
    if isinstance(target, np.ndarray):
        target = np.squeeze(target)
        if (target.ndim == 1 and
            target.shape[-1] == x_matrix.shape[-1]):
            return target
        else:
            raise ValueError('Target must be a 1D array with the same signal length.')
    
    if target == 'average':
        return nanmean(x_matrix, axis=0)
    
    if target == 'median':
        return nanmedian(x_matrix, axis=0)
    
    if target == 'max':
        interval_sum = np.add.reduceat(x_matrix, intervals, axis=-1)
        max_signal = np.argmax(interval_sum, axis=0) # signal with max intensity in each interval
        
        target = np.zeros_like(x_matrix[0,:])
        slices = intervals2slices(intervals, x_matrix.shape[-1])
        for i, slice_ in enumerate(slices):            
            target[slice_] = x_matrix[ max_signal[i], slice_]
        
        return target
        
    if target == 'average2':
        # icoshift implementation for this option is as follows:
        ## 1. Align samples against the 'mean' signal.
        ## 2. Using the aligned signals, for each interval:
        ##    - Take the mean, substract the minimum value
        ##    - Multiply the corrected mean by a factor, use it as target.
        target = nanmean(x_matrix, axis=0)
        aligned = icoshift(target, x_matrix, intervals)
        
        slices = intervals2slices(intervals)
        for i, slice_ in enumerate(slices):
            interval_mean = nanmean(aligned[:,slice_], axis=-1)
            target[slice_] = (interval_mean - np.min(interval_mean)) * average_multiplier
        
        return target # Return the target for another alignment.