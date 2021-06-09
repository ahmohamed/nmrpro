from nmrpro.classes.NMRSpectrum import NMRSpectrum, NMRSpectrum2D
from nmrpro.decorators import *
from nmrpro.exceptions import NMRShapeError, DomainError
from nmrpro.plugins.JSinput2 import Include

import numpy as np
from nmrpro.utils import str2bool

# Based on the implementations in NMRglue
# These functions return the apodization function, instead of the corrected data.

pi = np.pi


def EM(spec, lb=0.2):
    n = spec.shape[-1]
    sw = spec.udic[spec.ndim-1]['sw']
    
    lb = float(lb)
    #
    return np.exp(-pi * np.arange(n) * (lb/sw))

def GM(spec, g1=0.0, g2=0.0, g3=0.0):
    n = spec.shape[-1]
    sw = spec.udic[spec.ndim-1]['sw']
    
    g1, g2, g3 = float(g1), float(g2), float(g3)
    #
    e = pi * np.arange(n) * (g1/sw)
    g = 0.6 * pi * (g2/sw) * (g3 * (n - 1) - np.arange(n))
    return np.exp(e - g * g)

def GMB(spec, lb=0.0, gb=0.25):
    n = spec.shape[-1]
    sw = spec.udic[spec.ndim-1]['sw']
    
    lb, gb = float(lb), float(gb)
    
    a = pi * lb / sw
    b = -a / (2.0 * gb * n)
    return np.exp(-a * np.arange(n) - b * np.arange(n) ** 2)

def JMOD(spec, off=0.0, j=0.0, lb=0.0):
    n = spec.shape[-1]
    sw = spec.udic[spec.ndim-1]['sw']
    
    off, j, lb = float(off), float(j), float(lb)
    
    e = pi * lb / sw
    end = off + j * (n - 1) / sw
    
    return np.exp(-e * np.arange(n)) * np.sin(pi * off + pi * (end - off) * np.arange(n) / (n - 1))

def SP(spec, off=0.0, end=1.0, power=1):
    n = spec.shape[-1]
    
    off, end, power = float(off), float(end), float(power)        
    return np.power(np.sin(pi * off + pi * (end - off) * np.arange(n) /
                    (n - 1)), power)

def TM(spec, t1=0.0, t2=0.0):
    n = spec.shape[-1]
    
    t1, t2 = float(t1), float(t2)
    return np.concatenate((np.linspace(0, 1, int(t1)), np.ones(int(n - t1 - t2)), np.linspace(1, 0, int(t2)) ))

def TRI(spec, loc=-1, lHi=0.0, rHi=0.0): 
    n = spec.shape[-1]
    if loc == -1:
        loc = float(n)/2
        
    loc, lHi, rHi = float(loc), float(lHi), float(rHi) 
    return np.concatenate((np.linspace(lHi, 1., loc), np.linspace(1., rHi, n - loc + 1)[1:]))

########## MNOVA functions ##############

def gauss(spec, lb=0.0):
    n = spec.shape[-1]
    sw = spec.udic[spec.ndim-1]['sw']
    
    lb = float(lb)
    return np.exp(- (pi * np.arange(n))**2 * (lb/sw))

# TODO: shifted gauss
def shiftedGauss(spec, lb=0.0, shift=0):
    lb, shift = float(lb), float(shift)
    raise NotImplementedError

def sineBell(spec, off=0.0):
    off = float(off)
    return SP(spec, off, 1., 1)

def sineBellSq(spec, off=0.0):
    off = float(off)
    return SP(spec, off, 1., 2)

def hanning(spec):
    n = spec.shape[-1]
    return np.hanning(n)

def hamming(spec):
    n = spec.shape[-1]
    return np.hamming(n)

def trafincate(a, n):
    # f(t) = E/ (E2 + F2)
    # E = exp(-t/a), F = exp( (n-t)/a)
    # a = decay constant of the signal
    raise NotImplementedError




@jsCommand(['Processing', 'Apodization', 'Advanced apodization'], [1,2])
@interaction(inv=False, c=1., 
    em=(True, Include(EM)), gm=(False, Include(GM)), gmb=(False, Include(GMB)), 
    jmod=(False, Include(JMOD)), sp=(False, Include(SP)), tm=(False, Include(TM)),
    tri=(False, Include(TRI)) #TODO: argslabels
)
@perSpectrum
@perDimension
@forder(before=['FFT', 'ZF'])
def apod(spec, inv=False, c=1., *windows, **kwwindows):
    if not spec.udic[spec.ndim-1]['time']:
        raise DomainError('Cant perform apodization, spectrum is not in time domain')
    
    #
    windows += tuple( [v for v in kwwindows.values() if v] )
    
    windows = [w(spec) if callable(w) else w for w in windows]
    n = spec.shape[-1]
    
    if not all([w.shape[-1]==n for w in windows]):
        raise NMRShapeError('Apodization windows must have the same number of data points as the spectrum')
    
    total = np.ones(spec.shape[-1], spec.dtype)
    for w in windows:
        total *= w
    
    #Scale first point
    total[..., 0] = total[..., 0] * c
    if inv:
        total = 1 / total
        
    #
    return spec * total
    

@jsCommand(['Processing', 'Apodization', 'Expoenential line broadnening (auto)'], [1,2], args=None)
@perSpectrum
def _em_apod(s):
    return apod(s, w=lambda s: EM(s, 0.2))


