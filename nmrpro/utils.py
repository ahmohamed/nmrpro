from nmrglue.fileio.fileiobase import unit_conversion

def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")

def asComplex(re, im):
    return re + im*1j
    
def deinterlace(x):
    x_cos = x[1::2,:]
    x_sin = x[0::2,:]
    
    A = 1j*x_sin.real; A += x_cos.real
    B = 1j*x_sin.imag; B += x_cos.imag
    return A,B

def reinterlace(A,B):
    Xcos = asComplex(A.real, B.real);
    Xsin = asComplex(A.imag, B.imag);
    c = np.empty((Xcos.shape[0]+Xsin.shape[0], Xcos.shape[1]), dtype=Xcos.dtype)
    c[0::2,:] = Xsin
    c[1::2,:] = Xcos
    
    return c
    
    
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