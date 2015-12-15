from utils import listIndexOf, indexOf, get_package_name
from copy import deepcopy
import numpy as np
import traceback

class WorkflowStep:
    def __init__(self, f, *args, **kwargs):
        self._original = (f, args, kwargs)
        self._computed = (f, args, kwargs)
        self.__order = None
    
    def set_order(self, before=None, after=None, replaces=None, repeatable=False):
        if before == 'last':
            self.__order = 'last'
            return
        if before == 'first':
            self.__order = 'first'
            return
        
        self.__order = (before, after, replaces, repeatable)
    
    def del_order(self):
        self.__order = None
    
    @property
    def _order(self):
        if self.__order is not None:
            return self.__order
        
        f = self._original[0]
        if hasattr(f, '_order'):
            return f._order
        
        return (None, None, None, False)
    
    @property
    def operation_name(self):
        return get_package_name(self._original[0])
    
    @operation_name.setter
    def operation_name(self, val):
        self.__name = val
    
    def __call__(self, spec):
        f, args, kwargs = self._computed
        return f(spec, *args, **kwargs)

class Workflow:
    def __init__(self, from_flow=None):
        if from_flow is not None:
            self._steps = from_flow._steps
            self._stepnames = from_flow._stepnames
        else:
            self._steps = []
            self._stepnames = []
    
    def empty(self):
        return len(self._steps) == 0
    
    def append(self, step, order='auto'):
        if not isinstance(step, WorkflowStep):
            raise TypeError('Only WorkflowStep objects can be added to a workflow')
        
        replace = False
        if order == 'auto':
            order, replace = self._get_order_idx(step)
        
        
        if order == 'first':
            order = 0
        elif order == 'last':
            order = len(self._stepnames)

        if isinstance(order, int):
            if replace:
                self._steps[order] = step
                self._stepnames[order] = step.operation_name
            else:    
                self._steps.insert(order, step)
                self._stepnames.insert(order, step.operation_name)
        else:
            raise TypeError('Order must be an int, "first" or "last".')
        
    
    def execute(self, s):
        s = s.setData(reduce(lambda x, y: y(x), self._steps, s.original))
        return s
    
    def _get_order_idx(self, step):
        step_order = step._order
        stepname = step.operation_name
        stepcount = len(self._stepnames)
        if isinstance(step_order, str):
            if step_order == 'first':
                return 0, False

            if step_order == 'last':
                return stepcount, False
        
        before, after, replaces, repeatable = step_order
        
        #Repeatable
        if not repeatable:
            idx = indexOf(stepname, self._stepnames)
            
            if idx > -1: return idx, True
            
        # Replaces
        if replaces is not None:
            idx = listIndexOf(replaces, self._stepnames)
            if len(idx) > 0 and max(idx) > -1:
                return idx.index(max(idx)), True
        
        after_idx = 0
        if after is not None:
            idx = listIndexOf(after, self._stepnames, method='last')
            after_idx = max(idx) + 1
        
        before_idx = stepcount
        
        if before is not None:
            idx = listIndexOf(before, self._stepnames)
            
            before_idx = min(idx, key=lambda x: x if x >=0 else stepcount)
            if before_idx < 0: before_idx = stepcount
            
        
        if after_idx >  before_idx:
            raise ValueError('Incorrect step order. "before" & "after" are not compatible')
        
        return after_idx if after_idx > 0 else before_idx, False

class WFManager:
    @classmethod
    def excuteSteps(cls, steps, seed):
        
        #traceback.print_stack(limit=4)
        return reduce(lambda x, y: y(x), steps, seed)
    
    @classmethod
    def computeStep(cls, step, spec):
        
        if _islocked('no_transpose', spec):
            traceback.print_stack()
        wf = deepcopy(spec.history)
        all_steps = wf._steps
        idx, replace = wf._get_order_idx(step)
        
        
        before_idx = after_idx = idx
        if replace:
            after_idx += 1
        
        last = after_idx == len(all_steps)
        
        
        if before_idx == len(all_steps):
            input_ = spec
        else:
            input_ = spec.setData( cls.excuteSteps(all_steps[:before_idx], spec.original) )
            
            
        
        ret = step(input_)
        # If the function returned a computed step, execute it.
        if isinstance(ret, WorkflowStep):
            step._computed = ret._computed
            ret = step(input_)
        
        
        # If the function returned the processed spectrum, 
        # write the original function and arguments in the history.
        from .classes.NMRSpectrum import NMRSpectrum
        if isinstance(ret, NMRSpectrum):
            
            if ret.history._stepnames != wf._stepnames and (not ret.history.empty()):
                # The function modified the history itself.
                # history contains at least one operation.
                
                return ret # we trust the function.
            
            # By now, ret.history either contains the input_ history or is empty
            if len(all_steps[after_idx:]) > 0:
                
                output_ = cls.excuteSteps(all_steps[after_idx:], ret)
                ret = ret.setData(output_)
            
            wf.append(step)
            ret.history = wf
            
            
        
        #
        return ret
        
def _islocked(lock_name, s):
    if hasattr(s, 'spec_flags') and s.spec_flags.has_key(lock_name):
        return s.spec_flags[lock_name]
    
    return False