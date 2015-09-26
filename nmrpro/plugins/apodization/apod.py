from ...classes.NMRSpectrum import NMRSpectrum, NMRSpectrum2D
from ...decorators import inputs, both_dimensions, perSpectrum
import numpy as np
from ...utils import str2bool

# Based on the implementations in NMRglue
# These functions return the apodization function, instead of the corrected data.

pi = np.pi

def EM(spec, lb=0.2):
    n = spec.shape[-1]
    sw = spec.udic[spec.ndim-1]['sw']
    
    lb = float(lb)
    #print(lb,sw,n)
    return np.exp(-pi * np.arange(n) * (lb/sw))

def GM(spec, g1=0.0, g2=0.0, g3=0.0):
    n = spec.shape[-1]
    sw = spec.udic[spec.ndim-1]['sw']
    
    g1, g2, g3 = float(g1), float(g2), float(g3)
    #print(g1,g2,g3,sw,n)
    e = pi * np.arange(n) * (g1/sw)
    g = 0.6 * pi * (g2/sw) * (g3 * (n - 1) - np.arange(n))
    return np.exp(e - g * g)

def GMB(spec, lb=0.0, gb=0.0):
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
    return np.concatenate((np.linspace(0, 1, t1), np.ones(n - t1 - t2), np.linspace(1, 0, t2)))

def TRI(spec, loc='auto', lHi=0.0, rHi=0.0): 
    n = spec.shape[-1]
    if(loc == 'auto'):
        loc = float(n/2)
        
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



@both_dimensions
def args_to_function(s, args):
    def getQueryParams(prefix, query, separator = '_'):
        prefix = prefix + separator
        start=len(prefix)
        params = {k[start:]:v for (k,v) in query.items() if k.startswith(prefix)}
        return params
        
    def accumulate_apod_function(spec, flist, query):
        accumulative = np.ones(spec.shape[-1])
        for k in flist.keys():
            fun = flist[k](spec, **getQueryParams(k, query))
            accumulative *= fun
    
        return accumulative.astype(spec.dtype)
          
    f = {
        'em': EM,
        'sb': sineBell,
        'sb2': sineBellSq,
        'gm': GM,
        'gmb': GMB,
        'jmod': JMOD,
        'sp': SP,
        'tm': TM,
        'tri': TRI,
        'gauss': gauss,
        'sgauss': shiftedGauss,
        #TODO: Add the rest of functions
    }
    
    filtered_f = { k:f[k] for k in f.keys() if str2bool(args.get(k, "False")) }
    
    inv = str2bool(args.get('inv', "False"))
    c = float(args.get('c', "1.0"))
    apod = accumulate_apod_function(s, filtered_f, args)
    print('inv: ',inv)
    if inv:
        apod = 1 / apod
    
    apoded = apod * s
    
    if inv:
        apoded[..., 0] = apoded[..., 0] / c
    else:
        apoded[..., 0] = apoded[..., 0] * c
    
    return apoded
    

@perSpectrum
def webApod(nmrSpec, args):
    fn = lambda s:  args_to_function(s, args)
        
    if "apod" in nmrSpec.history.keys():
        return nmrSpec.fapplyAt(fn, "apod", "apod")
    return nmrSpec.fapplyAfter(fn, "apod", "original")


# Based on MVAPACK implementation
# TODO: Testing
# def apodize2d(fid,fun):
#     #Apply to direct dimension (columns)
#     wfid = np.apply_along_axis(fn, 1, fid)
#
#     #Indirect dimension
#     A,B = deinterlace(wfid)
#     A = np.apply_along_axis(fn, 0, A)
#     B = np.apply_along_axis(fn, 0, B)
#     wfid = reinterlace(A,B)
#
#     return wfid
