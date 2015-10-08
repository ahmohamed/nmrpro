import nmrglue.process.proc_base as p
import numpy as np
from ...classes.NMRSpectrum import NMRSpectrum, NMRSpectrum2D
from ...decorators import ndarray_subclasser, perSpectrum, both_dimensions
from ...utils import str2bool
from ..FFT.fft import fft_positive

from scipy.optimize import minimize
from scipy.stats import gmean

__all__ = ['ps', 'autops']

def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")


######## Objective functions ##########
# nD compatible
def max_integ(x, data):
    integ = np.trapz(p.ps(data, p0=x[0]*18000, p1=x[1]*18000).real)
    for i in range(1,data.udic['ndim']): integ = np.trapz(integ)
    return -integ

# nD compatible
def min_point(x, data):
    obj = -p.ps(data,p0=x[0]*18000, p1=x[1]*18000).real.min()
    return obj

def whiten(x, data):
    a = np.abs(p.ps(data, p0=x[0]*18000, p1=x[1]*18000).real)
    t = float(np.mean(a))
    return np.sum(a > t)

# nD Calculation is based on MVAPACK implementation
def min_entropy(x, data):
    if data.ndim > 1:
        return gmean([min_entropy(x, row) for row in data])
    
    _data = p.ps(data,p0=x[0]*18000, p1=x[1]*18000).real
    drv = np.absolute(np.diff(_data))
    hst = drv / sum(drv)
    g = np.ptp(data.real)
    penalty = np.sum( _data[_data<0]**2 ) * g
    
    entropy = np.sum(hst * np.log(hst)) + penalty
    return entropy


def peak_minima(x, s):
    s0 = p.ps(s, p0=x[0]*18000, p1=x[1]*18000)
    s = np.real(s0).flatten()

    i = np.argmax(s)
    peak = s[i]
    mina = np.min(s[i - 100:i])
    minb = np.min(s[i:i + 100])

    return np.abs(mina - minb)


def opt_ps(data, obj_fun):
    obj_0 = lambda x, data: obj_fun([x,0], data)
    phase0 = minimize(obj_0, (0,), method='Nelder-Mead', args=(data,)).x[0]
    
    obj_1 = lambda x, data: obj_fun([phase0,x], data)
    phase1 = minimize(obj_1, (0,), method='Nelder-Mead', args=(data,)).x[0]
    return phase0*18000,phase1*18000

def opt_ps0(data, obj_fun):
    obj_0 = lambda x, data: obj_fun([x,0], data)
    phase0 = minimize(obj_0, (0,), method='Nelder-Mead', args=(data,)).x[0]
    return phase0*18000,0

def opt_ps_sim(data, obj_fun):
    phase0,phase1 = minimize(
        obj_fun, (0.,0.),
        method='Nelder-Mead',
        args=(data,)
    ).x
    return phase0*18000,phase1*18000
       

def atan_ps0(data):
    left=300
    right=350
    a = b = c = d = 0
    win_size = 50

    a = np.sum(data.real[left:left+win_size])
    b = np.sum(data.imag[left:left+win_size])
    c = np.sum(data.real[-right:-(right+win_size)])
    d = np.sum(data.imag[-right:-(right+win_size)])


    angle = np.arctan((a-c)/(d-b))
    phase0 = angle*180/np.pi
    print(phase0)
    return phase0,0

# TODO: fix implementation of angle1
def atan_ps(data):
    left=300
    right=350
    win_size = 50


    a = np.sum(data.real[left:left+win_size])
    b = np.sum(data.imag[left:left+win_size])
    left += 50
    c = np.sum(data.real[left:left+win_size])
    d = np.sum(data.imag[left:left+win_size])

    angle0 = np.arctan2((a-c),(d-b)) *180/np.pi


    c = np.sum(data.real[-right:-right+win_size])
    d = np.sum(data.imag[-right:-right+win_size])
    right += 50
    a = np.sum(data.real[-right:-right+win_size])
    b = np.sum(data.imag[-right:-right+win_size])

    angle1 = np.arctan2((a-c),(d-b)) *180/np.pi


    left -=50; right -=50;
    N = data.shape[-1]

    phase1 = N*(angle1-angle0)/(N-left-right)
    phase0 = angle0-angle1*(angle1-angle0)/(N-left-right);
    
    return phase0,phase1


def atan(data, p0only):
    if p0only: return atan_ps0(data)
    return atan_ps(data)





@perSpectrum
@both_dimensions
def ps(spec, phc):
    corrected = ndarray_subclasser(p.ps)(spec, *phc)
    dim = corrected.udic['ndim']-1
    corrected.udic[dim]['phc'] = phc
    return corrected

@perSpectrum
@both_dimensions
def autops(spec, method = 'minpoint', p0only=False):
    objfn = {
        "entropy":min_entropy,
        "integ":max_integ,
        "minpoint":min_point,
        "peakmin":peak_minima,
        "whiten":whiten,
        "atan":None        
    }[method]
    
    if method is not None: # not atan
        opt_function = opt_ps0 if p0only else opt_ps
        phc = opt_function(spec, objfn)
        return ps(spec, phc).di()
    
    # atan
    phc = atan(spec, p0only)
    return ps(spec, phc).di()


@perSpectrum
@both_dimensions
def optimize_phase(spec, opt_function, obj_function, ret='phc'): # FIXME: can we do that?
    phc = opt_function(spec, obj_function)
    
    # is it important that phc caculations on F2 direction be done on F1 corrected?
    return ps(spec, phc).di()
    

@both_dimensions
def phc_from_args(spec, args):
    alg = args.get('a','opt')
    if alg == 'opt':
        opt = {
            'auto0':opt_ps0,
            'auto':opt_ps, 
            'autosim':opt_ps_sim,
        }[args.get('optfn','autosim')]
        
        objfn = {
            "entropy":min_entropy,
            "integ":max_integ,
            "minpoint":min_point,
            "peakmin":peak_minima,
            "whiten":whiten
        }[args.get('objfn','entropy')]
        
        return optimize_phase(spec, opt, objfn)
    
    if alg == 'atan':
        phc = atan(spec, str2bool(args.get('p0only', "False")))
    elif alg == 'man':
        phc = (float(args.get('p0',0)), float(args.get('p1',0)))
    
    return ps(spec, phc)


@perSpectrum
def webPhase(nmrSpec, args):
    ffted_spec = fft_positive(nmrSpec.original_data())
    corrected = phc_from_args(ffted_spec, args)
    
    phc = {}
    for i in range(0, corrected.udic['ndim']):
        phc['F'+ str(i+1)+ '_phc'] = corrected.udic[i]['phc']
    
    # print(phc)
    fn = lambda s: ps(s, **phc)
    
    if "phase" in nmrSpec.history.keys():
        return nmrSpec.fapplyAt(fn, "phase", "phase")
    return nmrSpec.fapplyAfter(fn, "phase", "FFT")
