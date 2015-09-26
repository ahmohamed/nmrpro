import nmrglue as ng
import numpy as np
import nmrglue.process.proc_bl as bl
from scipy.optimize import curve_fit
from ...decorators import perSpectrum, perRow
from ...exceptions import DomainError

def constant(data, last=10):
    n = data.shape[-1] * 10 / 100. + 1.
    corr = data.real[..., -n:].sum(axis=-1) / n
    return np.array([corr]).transpose()

@perRow
def median_filter(data, mw=200, sf=16, sigma=5):
    return bl.calc_bl_med(data.real, mw=mw, sf=sf, sigma=sigma)

#@perTrace? check NMRPipe 
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
def tophat(data, size):
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




@perSpectrum
def webBaseline(nmrSpec, args):
    ret = args.get('ret', 'cor') # return corrected spectrum
    algorithm = args.get('a','cbf')
    
    f_est = {
        ########## Python based methods ##############
        'cbf': lambda s: constant(s, float(args.get('last',10))),
        'med': lambda s: median_filter(s,
            mw=float(args.get('bl_mw',200)),
            sf=float(args.get('bl_sf',16)),
            sigma=float(args.get('bl_sigma',5))
        ),
        'polynom': lambda s: fit_series(s, series='polynomial', n=int(args.get('n',3))),
        'cos': lambda s: fit_series(s, series='cosine', n=int(args.get('n',3))),
        #'bern': lambda s: fit_series(s, series='bernestein', n=int(args.get('n',3))),
        'airpls': lambda s: airpls(s, n=int(args.get('n',1)), lambda_ = int(args.get('lambda',10))),
        'iter_polynom': lambda s: iterp(s, n=int(args.get('n',3))),
        'th': lambda s: tophat(s, size=int(args.get('size',100))),
    }[algorithm]
    
    if nmrSpec.is_time_domain()[-1]:
        raise DomainError('Spectrum must be in the time domain for Baseline correction.')
    
    if 'baseline' in nmrSpec.history.keys():
        nmrData = nmrSpec.getSpectrumAt('baseline', include=False)
    else:
        nmrData = nmrSpec
    
    est = f_est(nmrData)
    
    if ret == 'est':  # return estimated baseline
        return est
    else:
        fn = lambda s: s - est
        return nmrSpec.fapplyAt(fn, "baseline")

@perSpectrum    
def SOL(spec, args):
    def ones(spec, args):
        return np.ones(spec.shape[-1], spec.dtype)*spec
        
    fn = lambda s: ones(s, args)
    return spec.fapply(fn, "ones")




def baseline_old(data, args):

    if alg == "whit":
        # lamda =100, weight vector = ones(), order=1, 
        import bl_airPLS
        #np.ones should be replaced with a cwt scales!!
        return bl_airPLS.WhittakerSmooth(data, np.ones(data.shape[0]), 1) #look for default params from Mestrenova (from R, lambda=1e5)
    
    if alg == "tophat":
        return tophat(data)
    
    ########## R based methods ##############    
    return data



    
def tophat_old(data):
    from scipy import ndimage
    rl = data.real
    struct_pts = int(round(rl.size * 0.1))
    str_el = np.repeat([1], struct_pts)
    data.real = ndimage.white_tophat(rl,None, str_el)
    
    return data

def baseline_backup(data, args):
    alg = args.get('bl_a','cbf')
    prev = int(args.get('bl_prev',2))
    #import pdb; pdb.set_trace()
    
    ########## Python based methods ##############
    if alg == "cbf":
        last = float(args.get('bl_last',10))
        # last n points to estimate bl
        if prev == 0:  # return estimated baseline
            n = data.shape[-1] *  last/ 100. + 1.
            a=np.empty(data.shape[-1]);
            a.fill(data[..., -n:].sum(axis=-1) / n)
            return a
        
        if prev == 1:  # return corrected spectrum
            return bl.cbf(data.copy(), last)
        
        data = bl.cbf(data, last)
        return data
    
    if alg == "med":
        mw = float(args.get('bl_mw',200))
        sf = float(args.get('bl_sf',16))
        sigma = float(args.get('bl_sigma',5))
        
        #med window size =24, smooth wind size=16, sigma=5
        if prev == 0:  # return estimated baseline
            return bl.calc_bl_med(data.real, mw=mw, sf=sf, sigma=sigma)
        
        if prev == 1:  # return estimated baseline
            datacopy = data.real.copy()
            return bl.med(datacopy, mw=mw, sf=sf, sigma=sigma)
            
        data.real = bl.med(data.real, mw=mw, sf=sf, sigma=sigma)
        return data
    
    if alg == "polynom":
        n = int(args.get('bl_n',3))
        x = np.arange(0,data.shape[-1])
        z = np.polyfit(x, data.real, n)
        f = np.poly1d(z)
        
        if prev == 0:  # return estimated baseline
            return f(x)
        
        if prev == 1:  # return estimated baseline
            datacopy = data.real.copy()
            return datacopy - f(x)
        
        data.real = data.real - f(x)
        return data
    
    if alg == "cos":
        n = int(args.get('bl_n',3))
        x = np.arange(0,data.shape[-1])
        f = cos_series(n)
        params = curve_fit(f, x, data.real, p0=np.ones(n))[0]
        
        
        if prev == 0:  # return estimated baseline
            return f(x, *params)
        
        if prev == 1:  # return estimated baseline
            datacopy = data.real.copy()
            return datacopy - f(x, *params)
        
        data.real = data.real - f(x, *params)
        return data
        
    if alg == "bern":
        n = int(args.get('bl_n',3))
        x = np.arange(0,data.shape[-1])
        f = bern_series(n)
        params = curve_fit(f, x, data.real, p0=np.ones(n))[0]
        
        
        if prev == 0:  # return estimated baseline
            return f(x, *params)
        
        if prev == 1:  # return estimated baseline
            datacopy = data.real.copy()
            return datacopy - f(x, *params)
        
        data.real = data.real - f(x, *params)
        return data
    
    if alg == "airpls":
        n = int(args.get('bl_n',1))
        lambda_ = int(args.get('bl_lambda',10))
        
        # lamda =10, porder=1,iter=15 
        import bl_airPLS
        est = bl_airPLS.airPLS(data,10,4)
        
        if prev == 0:  # return estimated baseline
            return est
        
        if prev == 1:  # return estimated baseline
            datacopy = data.real.copy()
            return datacopy - est
        
        data.real = data.real - est
        return data
        
        
    if alg == "whit":
        # lamda =100, weight vector = ones(), order=1, 
        import bl_airPLS
        #np.ones should be replaced with a cwt scales!!
        return bl_airPLS.WhittakerSmooth(data, np.ones(data.shape[0]), 1) #look for default params from Mestrenova (from R, lambda=1e5)
    
    if alg == "iter_polynom":
        n = int(args.get('bl_n',3))
        
        # order=3,iter=100, tol=1e-3
        import bl_airPLS
        est = bl_airPLS.iter_polynom(data, n)
        if prev == 0:  # return estimated baseline
            return est
        
        if prev == 1:  # return estimated baseline
            datacopy = data.real.copy()
            return datacopy - est
        
        data.real = data.real - est
        return data
    
    if alg == "tophat":
        return tophat(data)
    
    

    ########## R based methods ##############    
    
    return data



def peak_pick(data, args):
    alg = args.get('pp_a','t')
    threshold = float(args.get('pp_t',0))
    segments = bool(args.get('pp_s',0))
        
    if alg == 'cwt':
        return {'peaks': find_peaks_cwt(data, np.array([8,16,32]), min_snr=16)}
    
    if alg == 't':
        peaks = ng.peakpick.find_all_thres_fast(data.real, threshold, [20,], False)
        
    if alg == 'c':
        peaks = ng.peakpick.find_all_connected(data.real, threshold, False)
        
    if not segments:
        return {peaks: [int(item) for sublist in peaks for item in sublist]}
    
    segs = [ng.peakpick.find_pseg_slice(data,l,0) for l in peaks]
    
    return {'peaks': [int(item) for sublist in peaks for item in sublist], 'segs':[[item.start,item.stop] for sublist in segs for item in sublist]}