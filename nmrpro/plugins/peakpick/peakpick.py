import nmrglue.analysis.peakpick as pp
from ...classes.NMRSpectrum import SpecFeature
import numpy as np
from scipy.signal import find_peaks_cwt
#from ...classes.NMRSpectrum import NMRSpectrum, DataUdic
from ...decorators import perSpectrum

#@inputs(NMRSpectrum)
@perSpectrum
def pick(spec, args):
    #print(args)
    alg = args.get('a','cwt')
        
    if alg == 'cwt':
        return  SpecFeature(
            {'peaks': find_peaks_cwt(spec.real, np.array([8,16,32]), min_snr=16)},
            spec)
    
    if alg == 't':
        peaks = pp.find_all_thres_fast(spec.real, float(args.get('thresh',0)), [20,], False)
        
    if alg == 'c':
        peaks = pp.find_all_connected(spec.real, float(args.get('thresh',0)), False)
        
    if not bool(args.get('seg',0)):
        ret = {'peaks': [int(item) for sublist in peaks for item in sublist]}
    else:
        segs = [pp.find_pseg_slice(spec, l, 0) for l in peaks]
        ret = {'peaks': [int(item) for sublist in peaks for item in sublist], 'segs':[[item.start,item.stop] for sublist in segs for item in sublist]}
    
    return SpecFeature(ret, spec)