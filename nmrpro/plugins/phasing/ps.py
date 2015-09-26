from nmrglue.process.proc_base import ps, fft_positive
import numpy as np
from ...classes.NMRSpectrum import NMRSpectrum, NMRSpectrum2D
from ...decorators import ndarray_subclasser, perSpectrum, both_dimensions
from ...utils import str2bool
from ..FFT.fft import fft_positive

from scipy.optimize import minimize
from scipy.stats import gmean

def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")


######## Objective functions ##########
# nD compatible
def max_integ(x, data):
    integ = np.trapz(ps(data, p0=x[0]*18000, p1=x[1]*18000).real)
    for i in range(1,data.udic['ndim']): integ = np.trapz(integ)
    return -integ

# nD compatible
def min_point(x, data):
    obj = -ps(data,p0=x[0]*18000, p1=x[1]*18000).real.min()
    return obj

def whiten(x, data):
    a = np.abs(ps(data, p0=x[0]*18000, p1=x[1]*18000).real)
    t = float(np.mean(a))
    return np.sum(a > t)

# nD Calculation is based on MVAPACK implementation
def min_entropy(x, data):
    if data.ndim > 1:
        return gmean([min_entropy(x, row) for row in data])
    
    _data = ps(data,p0=x[0]*18000, p1=x[1]*18000).real
    drv = np.absolute(np.diff(_data))
    hst = drv / sum(drv)
    g = np.ptp(data.real)
    penalty = np.sum( _data[_data<0]**2 ) * g
    
    entropy = np.sum(hst * np.log(hst)) + penalty
    return entropy


def peak_minima(x, s):
    s0 = ps(s, p0=x[0]*18000, p1=x[1]*18000)
    s = np.real(s0).flatten()

    i = np.argmax(s)
    peak = s[i]
    mina = np.min(s[i - 100:i])
    minb = np.min(s[i:i + 100])

    return np.abs(mina - minb)


def auto_ps(data, obj_fun):
    obj_0 = lambda x, data: obj_fun([x,0], data)
    phase0 = minimize(obj_0, (0,), method='Nelder-Mead', args=(data,)).x[0]
    
    obj_1 = lambda x, data: obj_fun([phase0,x], data)
    phase1 = minimize(obj_1, (0,), method='Nelder-Mead', args=(data,)).x[0]
    return phase0*18000,phase1*18000

def auto_ps0(data, obj_fun):
    obj_0 = lambda x, data: obj_fun([x,0], data)
    phase0 = minimize(obj_0, (0,), method='Nelder-Mead', args=(data,)).x[0]
    return phase0*18000,0

def auto_ps_sim(data, obj_fun):
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





@both_dimensions
def correct_phase(spec, phc):
    corrected = ndarray_subclasser(ps)(spec, *phc)
    dim = corrected.udic['ndim']-1
    corrected.udic[dim]['phc'] = phc
    return corrected

@both_dimensions
def optimize_phase(spec, opt_function, obj_function, ret='phc'): # FIXME: can we do that?
    phc = opt_function(spec, obj_function)
    
    # is it important that phc caculations on F2 direction be done on F1 corrected?
    return correct_phase(spec, phc).di()
    

@both_dimensions
def phc_from_args(spec, args):
    alg = args.get('a','opt')
    if alg == 'opt':
        opt = {
            'auto0':auto_ps0,
            'auto':auto_ps, 
            'autosim':auto_ps_sim,
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
    
    return correct_phase(spec, phc)


@perSpectrum
def webPhase(nmrSpec, args):
    ffted_spec = fft_positive(nmrSpec.original_data())
    corrected = phc_from_args(ffted_spec, args)
    
    phc = {}
    for i in range(0, corrected.udic['ndim']):
        phc['F'+ str(i+1)+ '_phc'] = corrected.udic[i]['phc']
    
    print(phc)
    fn = lambda s: correct_phase(s, **phc)
    
    if "phase" in nmrSpec.history.keys():
        return nmrSpec.fapplyAt(fn, "phase", "phase")
    return nmrSpec.fapplyAfter(fn, "phase", "FFT")


###############################################################
################# Backup methods. Deleted before release ######
def ps2d(data, p00, p01,p10,p11):
    #Apply to direct dimension (columns)
    data = ps(data, p00, p01)
    
    #Indirect dimension
    fn = lambda s: ps(s, p10, p11)
    A,B = deinterlace(data)
    A = np.apply_along_axis(fn, 0, A)
    B = np.apply_along_axis(fn, 0, B)
    data = reinterlace(A,B)
    
    return data

def whiten_backup(x, data):
    sp = ps(data,p0=x[0], p1=x[1])
    x = sp.real
    A = np.abs(sp)
    t =  np.mean(A)
    
    N = sum(x[-t < x < t])
    return -N

# ACME: Automated phase Correction based on Minimization of Entropy
import scipy as sp
def autophase(nmr_data, pc_init=None, algorithm='Peak_minima'):
    if pc_init is None:
        pc_init = [0, 0]

    fn = {
        'ACME': autophase_ACME,
        'Peak_minima': autophase_PeakMinima,
    }[algorithm]

    opt = sp.optimize.fmin(fn, x0=pc_init, args=(nmr_data.reshape(1, -1)[:500], ))
    return ps(nmr_data, p0=opt[0], p1=opt[1]), opt


# TODO: fix the need to data.reshape(1, -1)
def autophase_ACME(x, s):
    stepsize = 1

    n, l = s.shape
    phc0, phc1 = x

    s0 = ps(s, p0=phc0, p1=phc1)
    s = np.real(s0)
    maxs = np.max(s)

    # Calculation of first derivatives
    ds1 = np.abs((s[2:l] - s[0:l - 1]) / (stepsize * 2))
    p1 = ds1 / np.sum(ds1)

    # Calculation of entropy
    m, k = p1.shape

    for i in range(0, m):
        for j in range(0, k):
            if (p1[i, j] == 0):  # %in case of ln(0)
                p1[i, j] = 1

    h1 = -p1 * np.log(p1)
    h1s = np.sum(h1)

    # Calculation of penalty
    pfun = 0.0
    as_ = s - np.abs(s)
    sumas = np.sum(as_)

    if (sumas < 0):
        pfun = pfun + np.sum((as_ / 2) ** 2)

    p = 1000 * pfun

    # The value of objective function
    return h1s + p



def peak_minima2d(x, s):
    s0 = correct_phase(s, [(x[0]*18000, x[1]*18000),(x[2]*18000, x[3]*18000)])
    s = np.real(s0).flatten()

    i = np.argmax(s)
    peak = s[i]
    mina = np.min(s[i - 100:i])
    minb = np.min(s[i:i + 100])

    return np.abs(mina - minb)

def whiten2d(x, data):
    a = np.abs(correct_phase(data, [(x[0]*18000, x[1]*18000),(x[2]*18000, x[3]*18000)]).real)
    t = float(np.mean(a))
    print(x, data.shape)
    return np.sum(a > t)

def obj2d(x, data):
    a = np.abs(correct_phase(data, [(x[0]*18000, x[1]*18000),(x[2]*18000, x[3]*18000)]).real)
    t = float(np.mean(a))
    print(x, data.shape)
    return np.sum(a > t)

    
def opt2d(data, obj_fun):
    x = minimize(
        obj_fun, (0.,0., 0., 0.),
        method='Nelder-Mead',
        args=(data,)
    ).x
    return [(x[0]*18000, x[1]*18000),(x[2]*18000, x[3]*18000)]


