from nmrglue.fileio import bruker, pipe
from nmrglue.fileio.fileiobase import unit_conversion, uc_from_udic
from .utils import make_uc_pipe
from .NMRFileManager import get_files, find_pdata
from classes.NMRSpectrum import NMRSpectrum
import nmrglue.process.pipe_proc as pp
from nmrglue import __version__ as ng_version
from .exceptions import NoNMRDataError

ng_version = float(ng_version[:3])

def fromFile(file, format='auto'):
    if format == 'auto':
        files = get_files(file)
        
        if files is None:
            raise NoNMRDataError('The path supplied has no NMR spectra: %s' %file)
        elif len(files) == 1:
            return fromFile(*files[0])
        else:
            return [fromFile(*f) for f in files]
            
    method = {
        'Bruker': fromBruker,
        'Pipe': fromPipe
    }[format]

    return method(file)

def fromBruker(file, remove_filter=True, read_pdata=True):
    dic, data = bruker.read(file);
    if read_pdata:
        pdata_file = find_pdata(file, data.ndim)
        
        if(pdata_file is not None):
            procs, data = bruker.read_pdata(pdata_file)
        else: read_pdata = False
    
    if remove_filter and not read_pdata:
        if ng_version > 0.5:
            data = bruker.remove_digital_filter(dic, data, True)
        else:
            data = bruker.remove_digital_filter(dic, data)
    
    u = bruker.guess_udic(dic, data)    
    u["original_format"] = 'Bruker'
    u["Name"] = str(file)
    if(read_pdata):
        for i in range(0, data.ndim):
            u[i]['complex'] = False
            u[i]['freq'] = True
            u[i]['time'] = False
    
    uc  = [uc_from_udic(u, dim) for dim in range(0, data.ndim)]
    
    if read_pdata and 'procs' in procs.keys():
        proc_names = ['procs', 'proc2s']
        for i, uc_i in enumerate(uc[::-1]):
            if procs[proc_names[i] ] and procs[proc_names[i] ]['OFFSET']:
                uc_i._first = procs[proc_names[i] ]['OFFSET']
    
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
