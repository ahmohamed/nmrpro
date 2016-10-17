from numbers import Number
from collections import OrderedDict
import inspect

def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")

class Input(object):
    pass

class Panel(Input):
    def __init__(self, *args):
        self.args = args
    
    def to_dict(self):
        ret = OrderedDict()
        if not self.args: return ret
        
        for a in self.args:
            ret.update(a.to_dict())

        return ret
    
    def calculate(self, kwargs):
        for a in self.args:
            if a.varname in kwargs.keys():
                a.calculate(kwargs)
        
        return kwargs

class ArgsPanel(Input):
    def __init__(self, **kwargs):
        self.f = None
        self.kwargs = kwargs
    
    def get_panel(self):
        f = self.f 
        arg_defaults = get_args_defaults(self.f)
        labels = self.kwargs.pop('arglabels', {})
        panel = _parse_interactive_args(self.kwargs, labels, arg_defaults)
        return panel

        
class Include(Panel):
    def __init__(self, f):
        self.func = f
        
        panel = _parse_interactive_func(f)
        self.panel = _parse_interactive_func(f)
        self.args = self.panel.args

    def to_dict(self):
        ret = super(Include, self).to_dict()
        if self.args is not None:
            ret = _mangle_dict_keys(ret, self.func.__name__)
            
        return ret
    
    def calculate(self, kwargs):
        mangle = '$'+self.func.__name__
        func_args = {k.split('$')[0]:kwargs.pop(k)
                     for k in kwargs.keys() 
                     if k.endswith(mangle)}
        
        
        func_args = super(Include, self).calculate(func_args)
        
        def newf(*args, **kw):
            func_args.update(kw)
            return self.func(*args, **func_args)
        
        return newf
    
class Numeric(Input):
    def __init__(self, varname, label=None, val=None, _min=None, _max=None, step=1, unit=''):
        if label is None: label = varname
        
        self.varname = varname
        self.label = label
        self.val = val
        self._min = _min
        self._max = _max
        self.step = step
        self.unit = unit
    
    def to_dict(self): #TODO: unit, step (int,float)
        return {self.varname:[self.label, 0, [self.val, self._min, self._max, self.step]]}
    
    def calculate(self, kwargs):
        val = kwargs.pop(self.varname)
        
        try: kwargs[self.varname] = int(val)
        except ValueError:
            kwargs[self.varname] = float(val)
        
        return kwargs[self.varname]

class Boolean(Input):
    def __init__(self, varname, label=None, val=False):
        if label is None: label = varname
        
        self.varname = varname
        self.label = label
        self.val = val
    
    def to_dict(self):
        return {self.varname:[self.label, 1, self.val]}
    
    def calculate(self, kwargs):
        val = kwargs.pop(self.varname)
        kwargs[self.varname] = str2bool(val)
        return kwargs[self.varname]
    
class Text(Input):
    def __init__(self, varname, label=None, val=None):
        if label is None: label = varname
        
        self.varname = varname
        self.label = label
        self.val = val
    
    def to_dict(self):
        return {self.varname:[self.label, 2, self.val]}
    
    def calculate(self,kwargs):
        return kwargs[self.varname]

class Select(Input):
    def __init__(self, varname, label=None, *options):
        if label is None: label = varname
        
        self.varname = varname
        self.label = label
        self.options = options
    
    def to_dict(self):
        return {self.varname:[self.label, 3, Panel(*self.options).to_dict()]}
    
    def calculate(self, kwargs):
        val = kwargs.pop(self.varname)
        
        option = [o for o in self.options if o.varname == val][0]
        kwargs[self.varname] = option.calculate(kwargs)
        
        return kwargs[self.varname]
        
class Option(Input):
    def __init__(self, varname, label=None, toggle=None):
        if label is None:
            label = varname
        
        #Pattern {'Positive':Inlcude(fft_positive)}
        if isinstance(varname, Input):
            toggle = varname
            varname = label
        
        self.varname = varname
        self.label = label
        self.toggle = toggle
        
    def to_dict(self):
        if isinstance(self.toggle, Input):
            toggle = self.toggle.to_dict()
        else:
            toggle = {}
        return {self.varname:[self.label, toggle]}
    
    def calculate(self, kwargs):
        if isinstance(self.toggle, Input):
            toggle_val = self.toggle.calculate(kwargs)
        else:
            toggle_val = None
        
        if callable(toggle_val): # the toggle panel wan an IncludePanel, it returned a function
            return toggle_val
        
        return self.varname

class CheckboxToggle(Input):
    def __init__(self, varname, label=None, checked=False, toggle=None):
        if label is None: label = varname
        
        self.varname = varname  #TODO: Check if varname is IncludePanel
        self.label = label
        self.checked = checked
        self.toggle = toggle

    def to_dict(self):
        if isinstance(self.toggle, Input):
            toggle = self.toggle.to_dict()
        else:
            toggle = {}
            
        return {self.varname:[self.label, 4, [self.checked, toggle]]}
        
    def calculate(self, kwargs):
        checked = str2bool(kwargs[self.varname])
        
            
        if isinstance(self.toggle, Input):
            toggle_val = self.toggle.calculate(kwargs)
        else:
            toggle_val = None
        
        
        if checked and callable(toggle_val): # the toggle panel wan an IncludePanel, it returned a function
            kwargs[self.varname] = toggle_val
        else:
            kwargs[self.varname] = checked
        
        return kwargs[self.varname]

class Threshold(Input):
    def __init__(self, varname, label=None, axis='y'):
        if label is None: label = varname
        
        self.varname = varname
        self.label = label
        self.axis = axis

    def to_dict(self):
        return {self.varname:[self.label, 6, self.axis]}
    
    def calculate(self, kwargs):
        val = kwargs.pop(self.varname)
        kwargs[self.varname] = float(val)
        return kwargs[self.varname]

def _parse_interactive_func(f):    
    arg_defaults = get_args_defaults(f)
    
    if not all(hasattr(f, attr) for attr in ['__interactive', '__interactive_labels']):
        return _parse_interactive_args(arg_defaults)
    
    func_args = _parse_interactive_args(f.__interactive, f.__interactive_labels, arg_defaults)
    
    return func_args

def _parse_interactive_args(kwargs, kwlables=None, kwdefaults=None):
    kwlables = kwlables or {}
    kwdefaults = kwdefaults or {}
    
    all_ = []
    for k,v in kwargs.iteritems():
        _label = kwlables.pop(k, None)
        dft = kwdefaults.pop(k, None)
        all_.append(_abbrev(k, v, _label, dft))
    
    return Panel(*all_)
    
def _abbrev_single_value(varname, o, label, value):
    """Make widgets from single values, which can be used as parameter defaults."""
    if isinstance(o, basestring):
        return Text(varname, label, o)
    elif isinstance(o, dict):
        return Select(varname, label,
                      *[Option(var, lab) for lab, var in o.iteritems()]
                     )
    elif isinstance(o, bool):
        return Boolean(varname, label, o)
    elif isinstance(o, Number):
        return Numeric(varname, label, o)
    # elif isinstance(o, Include):
    #     o.varname = varname
    #     o.label = label
    #     return o
    elif isinstance(o, Input):
        return o
    else:
        return None


def _abbrev(varname, o, label, value):
    """Make widgets from abbreviations: single values, lists or tuples."""
    if isinstance(o, (list, tuple)) and len(o) > 1:
        if o and all(isinstance(x, basestring) for x in o):
            return Select(varname, label, #TODO: What about value?
                          *[Option(k) for k in o]
                         )
        elif o and all(isinstance(x, Number) for x in o):
            return Numeric(varname, label, value, *o)
        elif o and len(o) == 2 and isinstance(o[0], bool):
            return CheckboxToggle(varname, label, *o)
            
    else:
        return _abbrev_single_value(varname, o, label, value)
    
def _mangle_dict_keys(d, name):
    for k in d.keys():
        v = d.pop(k)
        if isinstance(v, dict):
            v = _mangle_dict_keys(v, name)
        
        d[k+'$'+str(name)] = v
    return d
    
def get_args_defaults(f):
    a = f.__argspec if hasattr(f, '__argspec') else inspect.getargspec(f)
    if a.defaults:
        arg_defaults = {v:a.defaults[i] for i,v in enumerate(a.args[-len(a.defaults):])}
    else:
        arg_defaults = {}
    
    return arg_defaults