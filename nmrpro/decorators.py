import sys
from copy import deepcopy
from classes.NMRSpectrum import NMRSpectrum, NMRDataset, DataUdic
from numpy import array
import re
from functools import wraps

def ndarray_subclasser(f):
    '''Function decorator. Forces functions to return the same ndarray
    subclass as its arguemets
    '''
    @wraps(f)
    def newf(*args, **kwargs):            
        ret = f(*args, **kwargs).view(type(args[0]))
        ret.__dict__ = deepcopy(args[0].__dict__)
        return ret
    newf.__name__ = f.__name__
    return newf

def workflow_manager(f):
    @wraps(f)
    def newf(input_, *args, **kwargs):
        if _islocked('workflow_lock', input_): return f(input_, *args, **kwargs)
        
        _lock('workflow_lock', input_)
        ret = f(input_, *args, **kwargs)
        _unlock('workflow_lock', input_, ret)
        
        if not isinstance(input_, NMRSpectrum):
            return ret # if the input is a DataUdic, no workflow info is kept
        
        # If the function returned the processed spectrum, 
        # write the original function and arguments in the history.
        if isinstance(ret, NMRSpectrum):
            if ret.history != input_.history and len(ret.history.keys()) > 1:
                # The function modified the history itself.
                # history.keys() > 1 means it contains at least one operation other than 'original'
                return ret # we trust the function.
            
            # By now, ret.history contains either the inputs history
            # or just the 'original' operation
            ret.history = spec.history
            step = WorkflowStep(f, *args[1:], **kwargs)
            ret.history[step.operation_name] = step
            return ret
        
        if isinstance(ret, WorkflowStep):
            step = ret
            step._original_args = tuple(f, *args[1:], **kwargs)
            ret = input_.applyStep(step)
            return ret

def both_dimensions(f, tp='auto'):
    '''Function decorator: applies the function to both dimemsions
    of a 2D NMR spectrum.

    Parameters:
    tp -- whether a hypercomplex transponse is performed.
             'auto' Automatically determine whether a hypercomplex is needed.
             'nohyper' Prevent a hypercomplex transpose.
             'hyper' Always perform a hypercomplex transpose.
    '''
    p = re.compile('F(\d+)_')
    
    def getQueryParams(prefix, query, separator = '_'):
        prefix = prefix + separator
        start=len(prefix)
        params = {k[start:]:v for (k,v) in query.items() if k.startswith(prefix)}
        
        if '' in params:  #remove empty kwargs. This may be used to signal processing only in a single dimension.
            del params['']
        return params
    
    def parseFnArgs(ndim, args, kwargs):
        if any( [re.match(p, k) for k in kwargs.keys()] ):
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
    @wraps(f)
    def newf(s, *args, **kwargs):
        # The purpose of no_transpose flag is to prevent nested decoration 
        # of both_dimensions. This may be the case when decorated functions call
        # other other ones, or in recursion.
        # In this case, the 'both_dimension' effect is kept only on the outer level.
        ###print(f.__module__, f.__name__, s.udic.get('no_transpose', False))
        if _islocked('no_transpose', s): return f(s, *args, **kwargs)
        
        if 'apply_to_dim' in kwargs:
            apply_to_dim = kwargs['apply_to_dim']
            del kwargs['apply_to_dim']
        else: apply_to_dim = range(0, s.udic['ndim'])
        
        
        Fn_args, Fn_kwargs = parseFnArgs(s.udic['ndim'], args, kwargs)
        
        _lock('no_transpose', s)
        ret = s
        #ret = f(s, *Fn_args[0], **Fn_kwargs[0]).tp(flag=tp, copy=False)
        for i in range(s.udic['ndim'] -1, -1, -1): # loop over dims in reverse order.
            if i in apply_to_dim:
                ret = f(ret, *Fn_args[i], **Fn_kwargs[i])
            ret = ret.tp(flag=tp, copy=False)
        
        _unlock('no_transpose', s, ret)
        return ret

    return newf
    

#TODO: write test with and without additional arguments (*args, **kwargs).
def perSpectrum(f):
    def proc_spec(*new_args, **kwargs):
        if not isinstance(new_args[0], DataUdic):
            raise TypeError('First argument is not a spectrum (DataUdic object)')
        
        # TODO: workflow manager
        ret = f(*new_args, **kwargs)
        if isinstance(ret, NMRSpectrum) and hasattr(new_args[0], "__s_id__"):
            ret.__s_id__ = new_args[0].__s_id__
        return ret
    
    def proc_speclist(*args, **kwargs):
        speclist = args[0]
        return [proc_spec(*((s,)+args[1:]), **kwargs) for s in speclist]
     
    @wraps(f)
    def newf(*args, **kwargs):
        if isinstance(args[0], list):
            return proc_speclist(*args, **kwargs)
        
        if isinstance(args[0], NMRDataset):
            dataset = args[0]
            dataset.specList = proc_speclist(*args, **kwargs)
            return dataset
        
        return proc_spec(*args, **kwargs)
        

    return newf

def perRow(f):
    @wraps(f)
    def newf(*args, **kwargs):
        if isinstance(args[0], DataUdic):
            if args[0].udic['ndim'] > 1:
                return array([f(*((v,) + args[1:]), **kwargs) for i,v in enumerate(args[0])])
            else:
                return f(*args, **kwargs)
        else:
            raise ValueError('First argument is not a spectrum.')
    
    return newf
    
#### Helper functions ###
def _lock(lock_name, *specs):
    for s in specs:
        if hasattr(s, 'udic'):
            s.udic[lock_name] = True

def _unlock(lock_name, *specs):
    for s in specs:
        if hasattr(s, 'udic') and s.udic.has_key(lock_name):
            del s.udic[lock_name]

def _islocked(lock_name, s):
    if hasattr(s, 'udic') and s.udic.has_key(lock_name):
        return s.udic[lock_name]
    
    return False