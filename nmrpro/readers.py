from nmrglue.fileio import bruker, pipe
from nmrglue.fileio.fileiobase import unit_conversion, uc_from_udic
from .utils import make_uc_pipe
from .NMRFileManager import find_pdata
from classes.NMRSpectrum import NMRSpectrum
def fromFile(file, format):
    method = {
        'Bruker': fromBruker,
        'Pipe': fromPipe
    }[format]

    return method(file)

def fromBruker(file, remove_filter=True, read_pdata=True):
    dic, data = bruker.read(file);
    if(read_pdata):
        pdata_file = find_pdata(file, data.ndim)
        
        if(pdata_file is not None):
            data = bruker.read_pdata(pdata_file)[1]
        else: read_pdata = False
    
    if remove_filter and not read_pdata:
        data = bruker.remove_digital_filter(dic, data, True)

    u = bruker.guess_udic(dic, data)
    u["original_format"] = 'Bruker'
    u["Name"] = str(file)
    if(read_pdata):
        for i in range(0, data.ndim):
            u[i]['complex'] = False
            u[i]['freq'] = True

    uc = []
    for i in range(0, data.ndim):
        acqus = ['acqus', 'acqu2s', 'acqu3s', 'acqu4s'][i]
        car = dic[acqus]['O1']
        sw = dic[acqus]['SW_h']
        size = u[i]['size']
        obs = dic[acqus]['BF1']
        cplx = u[i]['complex']
        uc.append(unit_conversion(size, cplx, sw, obs, car))

    return NMRSpectrum(data, udic=u, uc=uc)

def fromPipe(file):
    dic, data = pipe.read(file)
    if dic['FDTRANSPOSED'] == 1.:
        dic, data = pp.tp(dic, data, auto=True)

    u = pipe.guess_udic(dic, data)
    u["original_format"] = 'Pipe'
    u["Name"] = str(file)
    
    uc = [make_uc_pipe(dic, data, dim) for dim in range(0, data.ndim)]
    return NMRSpectrum(data, u, uc=uc)
