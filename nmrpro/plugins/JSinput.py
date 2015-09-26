def num(label, val=None, _min=None, _max=None, step=1, unit=''):
    return [label, 0, [val, _min, _max, step]]

def boolean(label, val=False):
    return [label, 1, val]

def text(label, val=None):
    return [label, 2, val]

def select(label, fields, field_label="Parameters"):
    return [label, 3, dict(fields)]

def option(label, args={}):
    return [label, args]

def checkbox_option(label, checked, args={}):
    return [label, 4, [checked, args]]

def threshold(label, axis):
    return [label, 6, axis]
    
#Remove or label
def multiselect(label, options):
    return [label, -1, dict(options)]
