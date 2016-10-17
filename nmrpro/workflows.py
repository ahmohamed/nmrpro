from utils import listIndexOf, indexOf, get_package_name
import numpy as np

class WorkflowStep:
    def __init__(self, f, *args, **kwargs):
        self.query_params = kwargs.pop('query_params', None)
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
    
    
    
    @property
    def query_params(self):
        return '&'.join(s.query_params for s in self._steps)
    
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
