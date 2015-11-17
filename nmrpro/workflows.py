from utils import listIndexOf, indexOf

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
        
        if hasattr(self._original[0], '_order'):
            return self._original[0]._order
        
        return 'last'
    
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
        
        if order == 'auto':
            order = self._get_order_idx(step)
        
        
        if order == 'first':
            order = 0
        elif order == 'last':
            order = len(self._stepnames)

        if isinstance(order, int):
            self._steps.insert(order, step)
            self._stepnames.insert(order, step.operation_name)
        else:
            raise TypeError('Order must be an int, "first" or "last".')
        
        if step.operation_name == 'apod':
            print ('apod',self._stepnames)
        
    
    def execute(self, s):
        s = s.setData(reduce(lambda x, y: y(x), self._steps, s.original))
        return s
    
    def _get_order_idx(self, step):
        step_order = step._order
        stepname = step.operation_name
        if isinstance(step_order, str):
            if step_order == 'first':
                return 0

            if step_order == 'last':
                return len(self._stepnames)
        
        before, after, replaces, repeatable = step_order
        
        #Repeatable
        if not repeatable:
            idx = indexOf(stepname, self._stepnames)
            if idx > -1: return idx
            
        # Replaces
        if replaces is not None:
            idx = listIndexOf(replaces, self._stepnames)
            if len(idx) > 0 and max(idx) > -1:
                return idx.index(max(idx))
        
        after_idx = 0
        if after is not None:
            idx = listIndexOf(after, self._stepnames, method='last')
            after_idx = max(idx) + 1
        
        before_idx = len(self._stepnames)
        if before is not None:
            idx = listIndexOf(before, self._stepnames)
            before_idx = min(idx)
            if before_idx < 0: before_idx = len(self._stepnames)
        
        if after_idx >  before_idx:
            raise ValueError('Incorrect step order. "before" & "after" are not compatible')
        
        return after_idx if after_idx > 0 else before_idx