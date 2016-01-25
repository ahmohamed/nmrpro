import nmrglue.process.proc_base as p
import numpy as np
from nmrpro.classes.NMRSpectrum import NMRSpectrum, NMRSpectrum2D
from nmrpro.decorators import *
from nmrpro.exceptions import DomainError
from nmrpro.utils import str2bool
from nmrpro.plugins.FFT.fft import fft_positive
from nmrpro.workflows import WorkflowStep

from scipy.optimize import minimize
from scipy.stats import gmean

__all__ = ['ps', 'autops']


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
    
    return phase0,0

# TODO: fix implementation of angle1
# Nothing wrong with the implementation?, however the method is not stable.
# See if we need to supply fft or not. di or not.
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


@jsCommand(['Processing', 'Phase Correction', 'Manual phase correction'], [1,2])
@perSpectrum
@perDimension
def ps(spec, p0=0, p1=0):
    dim = spec.udic['ndim']-1
    if spec.udic[dim]['time']:
        raise DomainError('Spectrum must be in the time domain for Phase correction.')
        
    corrected = ndarray_subclasser(p.ps)(spec, p0, p1)    
    corrected.udic[dim]['phc'] = (p0, p1)
    return corrected

@perDimension
def _optimize_phase(spec, objfn, p0only):
    if objfn is None: #atan
        phc = atan(spec, p0only)
    else:    
        opt_function = opt_ps0 if p0only else opt_ps
        phc = opt_function(spec, objfn)
    
    return ps(spec, *phc).di()

@jsCommand(['Processing', 'Phase Correction', 'Automatic phase correction'], [1,2], args=None)
@jsCommand(['Processing', 'Phase Correction', 'Advanced phase correction'], [1,2])
@interaction(method={'Entropy minization':'entropy', 'Intrgration maximization':'integ',
    'Minimum point maximization':'minpoint', 'Peak minima maximization':'peakmin',
    'Whitening':'whiten', 'Autmatic using arctan':'atan'}, 
    p0only=False
)
@perSpectrum
def autops(spec, method = 'minpoint', p0only=False):
    objfn = {
        "entropy":min_entropy,
        "integ":max_integ,
        "minpoint":min_point,
        "peakmin":peak_minima,
        "whiten":whiten,
        "atan":None  #TODO
    }[method]
    
    ffted_spec = fft_positive(spec.original_data())
    corrected = _optimize_phase(ffted_spec, objfn, p0only)
    phc = {}
    for i in range(0, corrected.udic['ndim']):
        phc['F'+ str(i+1)+ '_p0'] = corrected.udic[i]['phc'][0]
        phc['F'+ str(i+1)+ '_p1'] = corrected.udic[i]['phc'][1]
    
    
    return WorkflowStep(ps, **phc)
    