import nmrglue as ng
import numpy as np
import nmrglue.process.proc_bl as bl
from scipy.optimize import curve_fit
from nmrpro.decorators import *
from nmrpro.exceptions import DomainError
from nmrpro.workflows import WorkflowStep
from nmrpro.plugins.JSinput2 import ArgsPanel, Include


#TODO: last is a numUnit, currently in %
# Another way is to be a region, which can either be selected interactively, or as a numUnit.
def constant(data, last=10):
    n = data.shape[-1] * 10 / 100. + 1.
    corr = data.real[..., -n:].sum(axis=-1) / n
    return np.array([corr]).transpose()

@perRow
def median_filter(data, mw=200, sf=16, sigma=5):
    return bl.calc_bl_med(data.real, mw=mw, sf=sf, sigma=sigma)

#TODO: @perRow? check NMRPipe 
def fit_series(data, series, n):    
    f = {
        'polynom': poly_series(n),
        'cos': cos_series(n),
        'bern': bern_series(n),
    }[series]
    
    x = np.arange(0,data.shape[-1])
    params = curve_fit(f, x, data.real, p0=np.ones(n))[0]
    
    return f(x, *params)
    
def airpls(data, n=1, lambda_ =10):
    import bl_airPLS
    return bl_airPLS.airPLS(data.real, lambda_, n)
    
def iterp(data, n):
    import bl_airPLS
    return bl_airPLS.iter_polynom(data.real, n)
        

@perRow
def tophat(data, size=100):
    from scipy.ndimage import grey_dilation, grey_erosion
    #if data.ndim > 1 and size is not tuple:
    #    size = (size,) * data.ndim    
    return grey_dilation(grey_erosion(data.real, size), size)

def cos_series(order):
    def fun(x, *params):
        ret = 0
        for i in range(0, order):
            ret = ret + params[i]* np.cos(i*x)
    
        return ret

    return fun

def poly_series(order):
    def fun(x, *params):
        ret = 0
        for i in range(0, order):
            ret = ret + (params[i]* (x**i))
    
        return ret

    return fun

def bern_series(order):
    def fun(x, *params):
        ret = 0
        for i in range(0, order):
            ret = ret + (params[i] * ( (1-x) ** (order-1-i) ) * (x**i))
    
        return ret

    return fun





# TODO: add poly_series
@jsCommand(['Processing', 'Baseline Correction', 'Advanced baseline correction 2D'], [2],
    args=ArgsPanel(method={
        'Constant':Include(constant), 'Median':Include(median_filter)
    })
)
@jsCommand(['Processing', 'Baseline Correction', 'Advanced baseline correction'], [1],
    args=ArgsPanel(method={
        'Constant':Include(constant), 'Median':Include(median_filter),
        'Iterative Polynomial':Include(iterp), 'airPLS':Include(airpls),
        'Tophat':Include(tophat)
    })
)
@jsCommand(['Processing', 'Baseline Correction', 'Constant Baseline Correction'], [1,2], args=None)
@perSpectrum
def baseline(nmrSpec, method='auto', ret='corrected'):
    dim = nmrSpec.udic['ndim'] - 1 
    if nmrSpec.udic[dim]['time']:
        raise DomainError('Spectrum must be in the time domain for Baseline correction.')
    
    if method == 'auto':
        method = constant
    
    est = method(nmrSpec)
    if ret == 'baseline':  # return estimated baseline
        return est

    return WorkflowStep(np.subtract, est)


