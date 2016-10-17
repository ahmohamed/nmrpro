import nmrglue.analysis.peakpick as pp
from nmrpro.classes.NMRSpectrum import SpecFeature
import numpy as np
from scipy.signal import find_peaks_cwt
from nmrpro.decorators import *
from nmrpro.plugins.JSinput2 import ArgsPanel, Include, Threshold

__all__ = ['pick']

@perSpectrum
def _peak_cwt(spec, min_snr=16): #TODO: wavelet widths
    pk_list = find_peaks_cwt(spec.real, np.array([8,16,32]), min_snr=min_snr)
    feature = {'peaks':pk_list}
    return SpecFeature(feature, spec)

@jsCommand(['Analysis', 'Peak Picking', 'Peaks below a Threshold'], [1])
@interaction(threshold = Threshold('threshold'), msep=20)
@perSpectrum
def _peak_threshold(spec, threshold=0, msep=20):
    peaks = pp.find_all_thres_fast(spec.real, threshold, [msep,], False)
    pk_list = [int(item) for sublist in peaks for item in sublist]
    feature = {'peaks':pk_list}
    return SpecFeature(feature, spec)

@interaction(threshold = Threshold('threshold'))
@perSpectrum
def _peak_connected(spec, threshold=0):
    peaks = pp.find_all_connected(spec.real, threshold, False)
    pk_list = [int(item) for sublist in peaks for item in sublist]
    feature = {'peaks':pk_list}
    return SpecFeature(feature, spec)

def _segments(spec, peaks):
    segs = [pp.find_pseg_slice(spec, p, 0) for p in peaks]
    return [[item.start,item.stop] for sublist in segs for item in sublist]


@jsCommand(['Analysis', 'Peak Picking', 'Custom Peak Picking'], [1],
    args = ArgsPanel(method={
        'Threshold': Include(_peak_threshold),
        'Connected segments': Include(_peak_connected),
        'Continuous wavelet transform':Include(_peak_cwt)
    })
)
@jsCommand(['Analysis', 'Peak Picking', 'Automatically using CTW'], [1], args=None)
@perSpectrum
def pick(spec, method='cwt', find_segments=False):
    if method == 'cwt':
        method = _peak_cwt
    
    spec_feature = method(spec)
    if find_segments:
        segs = _segments(spec, spec_feature.data['peaks'])
        spec_feature.data['segs'] = segs
        
    return spec_feature
    
