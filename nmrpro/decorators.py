import sys
from copy import deepcopy
from classes.NMRSpectrum import NMRSpectrum, NMRDataset, DataUdic
from numpy import array

def inputs(type_):
    '''Function decorator. Checks decorated function's arguments are
    of the expected types.

    Parameters:
    types -- The expected types of the inputs to the decorated function.
             Must specify type for each parameter.

    '''
    def decorator(f):
        def newf(*args):      
            if not isinstance(args[0], type_):
                if isinstance(args[0], NMRDataset) and issubclass(type_, DataUdic):
                    dataset = args[0]
                    # arglist = args[1:]
                    dataset.specList = [f(*((s,)+args[1:])) for s in dataset]
                    return dataset
                else:
                    msg = info(f.__name__, type_, type(args[0]), 0)
                    print >> sys.stderr, 'TypeWarning: ', msg
            return f(*args)
        newf.__name__ = f.__name__
        return newf
    return decorator


def ndarray_subclasser(f):
    '''Function decorator. Forces functions to return the same ndarray
    subclass as its arguemets
    '''
    def newf(*args, **kwargs):            
        ret = f(*args, **kwargs).view(type(args[0]))
        ret.__dict__ = deepcopy(args[0].__dict__)
        return ret
    newf.__name__ = f.__name__
    return newf

def both_dimensions(f, tp='auto'):
    '''Function decorator: applies the function to both dimemsions
    of a 2D NMR spectrum.

    Parameters:
    tp -- whether a hypercomplex transponse is performed.
             'auto' Automatically determine whether a hypercomplex is needed.
             'nohyper' Prevent a hypercomplex transpose.
             'hyper' Always perform a hypercomplex transpose.
    '''
    def getQueryParams(prefix, query, separator = '_'):
        prefix = prefix + separator
        start=len(prefix)
        params = {k[start:]:v for (k,v) in query.items() if k.startswith(prefix)}
        return params
    
    def parseFnArgs(ndim, args, kwargs):
        if(getQueryParams('F1', kwargs)):
            Fn_kwargs = [ getQueryParams('F' + str(i+1), kwargs) for i in range(0, ndim) ]
        else:
            Fn_kwargs = [ kwargs for i in range(0, ndim) ]
        

        Fn_args = []
        [Fn_args.append([]) for j in range(0, ndim)]
        
        for i in range(0, len(args)):
            if type(args[i]) is dict and getQueryParams('F1', args[i]):
                for j in range(0, ndim):
                    Fn_args[j].append(getQueryParams('F' + str(j+1), args[i]))
            else:
                for j in range(0, ndim):
                    Fn_args[j].append(args[i])
        
            if i == len(args)-1: Fn_args = [tuple(Fn_args[j]) for j in range(0, ndim)]
            
        return (Fn_args, Fn_kwargs)           
                
    #TODO: do another option for analysis functions (the ones that doesn't return a spec).
    def newf(s, *args, **kwargs):
        # The purpose of no_transpose flag is to prevent nested decoration 
        # of both_dimensions. This may be the case when decorated functions call
        # other other ones, or in recursion.
        # In this case, the 'both_dimension' effect is kept only on the outer level.
        print(f.__module__, f.__name__, s.udic.get('no_transpose', False))
        if(s.udic.get('no_transpose', False)): return f(s, *args, **kwargs)
        
        s.udic['no_transpose'] = True
        Fn_args, Fn_kwargs = parseFnArgs(s.udic['ndim'], args, kwargs)
        
        ret = f(s, *Fn_args[0], **Fn_kwargs[0]).tp(flag=tp, copy=False)
        for i in range(1, s.udic['ndim']):
            ret = f(ret, *Fn_args[i], **Fn_kwargs[i]).tp(flag=tp, copy=False)
        
        s.udic['no_transpose'] = False    
        ret.udic['no_transpose'] = False
        return ret
    newf.__name__ = f.__name__
    return newf

# TODO: @inputs(NMRSpectrum)
def outputSpec(f, copy=False, preview=False):
    '''Function decorator. decides whther to copy or overwrite
    the input spectrum.
    '''
    @inputs(NMRSpectrum)
    def copySpec(s):
        s_ = s.copy()
        s_.__dict__ = deepcopy(s.__dict__)
        return s_
    
    def newf(*args):
        sid_factor = -1 if preview else 0
        if copy:
            s_copy = copySpec(args[0])
            ret = f(*((s_copy,)+args[1:]))
        else:
            ret = f(*args)
            if isinstance(ret, NMRSpectrum):
                ret.__s_id__ = sid_factor * args[0].__s_id__
            elif len(ret) == len(args[0]) and isinstance(ret[0], NMRSpectrum): # A list of spectra (Dataset, Sampleset)
                for a,b in zip(ret, args[0]):
                    a.__s_id__ = sid_factor * b.__s_id__

        return ret
    return newf


#TODO: write test with and without additional arguments.
def perSpectrum(f):
    def proc_spec(*new_args):
        if not isinstance(new_args[0], DataUdic):
            raise TypeError('First argument is not a spectrum (DataUdic object)')
        
        
        ret = f(*new_args)
        if isinstance(ret, NMRSpectrum) and hasattr(new_args[0], "__s_id__"):
            ret.__s_id__ = new_args[0].__s_id__
        return ret
    
    def proc_speclist(*args):
        speclist = args[0]
        return [proc_spec(*((s,)+args[1:])) for s in speclist]
        
    def newf(*args):
        if isinstance(args[0], list):
            return proc_speclist(*args)
        
        if isinstance(args[0], NMRDataset):
            dataset = args[0]
            dataset.specList = proc_speclist(*args)
            return dataset
        
        return proc_spec(*args)
        
    newf.__name__ = f.__name__
    return newf

def perRow(f):
    def newf(*args, **kwargs):
        print(args)
        if isinstance(args[0], DataUdic):
            if args[0].udic['ndim'] > 1:
                return array([f(*((v,) + args[1:]), **kwargs) for i,v in enumerate(args[0])])
            else:
                return f(*args, **kwargs)
        else:
            raise ValueError('First argument is not a spectrum.')
    newf.__name__ = f.__name__
    return newf 