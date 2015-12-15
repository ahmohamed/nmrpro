from .decorators import wraps
from .classes import DataUdic
import numpy as np
from copy import deepcopy
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
import rpy2.robjects as robjects
from rpy2.robjects import reval, r
import rpy2.robjects.numpy2ri
rpy2.robjects.numpy2ri.activate()

__all__ = ['library', 'R_function', 'reval', 'r']
def library(lib):
    importr(lib)


def R_function(f):
    @wraps(f)
    def rfunc(s, *args, **kwargs):
        if not isinstance(s, DataUdic):
            return f(s, *args, **kwargs)
        
        ret = f(s, *args, **kwargs)
        if isinstance(ret, robjects.vectors.Vector):
            try:
                ret = np.asarray(list(ret)).reshape(s.shape).view(type(s))
                ret.__dict__ = deepcopy(s.__dict__)
            except ValueError:
                pass #TODO: warn('R vector doesnt have same shape as the input')
        
        return ret
    return rfunc
