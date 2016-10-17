from nmrglue.fileio.fileiobase import unit_conversion
import inspect

def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")

def num_unit(s):
    numeric = '0123456789-.'
    for i,c in enumerate(s+' '):
        if c not in numeric:
            break
    try:
        number = float(s[:i])
        unit = s[i:].lstrip()
    except ValueError:
        raise ValueError('Incorrect number-unit format %s. Examples: 1ppm, 10hz, 5ms' %s)
    return number, unit    


def get_package_name(func):
    full_name = inspect.getmodule(func).__package__
    return full_name.split('.')[-1]

def import_from(module, name):
    module = __import__(module, fromlist=[name])
    return getattr(module, name)


def indexOf(element, ls, method='first'):
    if method == 'first':
        try: return ls.index(element)
        except ValueError: return -1
    
    if method == 'last':
        try: return len(ls) - ls[::-1].index(element) - 1
        except ValueError: return -1
    
    if method == 'all':
        indices = [i for i, x in enumerate(ls) if x == element]
        if len(indices) > 0:
            return indices
        else: return -1
    
    raise ValueError('indexOf: method should be first, last or all')
    
def listIndexOf(element_ls, ls, method='first'):
    if method == 'all':
        raise ValueError('Method all cannot be used with listIndexOf')
    
    if isinstance(element_ls, list):
        return [indexOf(e, ls) for e in element_ls]
    else:
        return [indexOf(element_ls, ls, method)]




def make_uc_pipe(dic, data, dim=-1):
    if dim == -1:
        dim = data.ndim - 1     # last dimention

    fn = "FDF" + str(int(dic["FDDIMORDER"][data.ndim - 1 - dim]))
    size = float(data.shape[dim])

    # check for quadrature in indirect dimentions
    if (dic[fn + "QUADFLAG"] != 1) and (dim != data.ndim - 1):
        size = size / 2.
        cplx = True
    else:
        cplx = False

    sw = dic[fn + "SW"]
    if sw == 0.0:
        sw = 1.0
    obs = dic[fn + "OBS"]
    if obs == 0.0:
        obs = 1.0

    car = dic[fn + "CAR"] * obs
    # NMRPipe keeps the carrier constant during extractions storing the
    # location of this point as CENTER.  This may not be the actual "center" of
    # the spectrum and may not even be a valid index in that dimension. We need
    # to re-center the carrier value so that actually represents the
    # frequency of the central point in the dimension.
    if dic[fn + "X1"] != 0. or dic[fn + "XN"] != 0.:
        car = car + sw / size * (dic[fn + "CENTER"] - 1. - size / 2.)
    return unit_conversion(size, cplx, sw, obs, car)