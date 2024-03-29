from nmrglue.fileio import bruker, pipe
from nmrglue.fileio.fileiobase import unit_conversion, uc_from_udic
from .utils import make_uc_pipe
from .NMRFileManager import get_files, find_pdata
from classes.NMRSpectrum import NMRSpectrum
import nmrglue.process.pipe_proc as pp
from nmrglue import __version__ as ng_version
from .exceptions import NoNMRDataError

from .constants import BRUKER_FORMAT
from .constants import AUTODETECT_FORMAT
from .constants import PIPE_FORMAT
from .constants import SPARKY_FORMAT

ng_version = float(ng_version[:3])

def get_name(file):
    filename = os.path.basename(file)
    return os.path.splitext(filename)[0]

def fromFile(*args, **kwargs):
    results = [spectra for spectra in _fromFile(*args, **kwargs)  if spectra is not None]
    if not results:
        raise NoNMRDataError("The path supplied has no NMR spectra.")
    if len(results) == 1:
        return results[0]
    return results

def _fromFile(file, format=AUTODETECT_FORMAT):
    if format == AUTODETECT_FORMAT:
        gen = (
            result
            for file, format in get_files(file)
            for result in _fromFile(file, format=format)
        )
    elif format == BRUKER_FORMAT:
        gen = (fromBruker(file), )
    elif format == PIPE_FORMAT:
        gen = (fromPipe(file), )
    else:
        raise ValueError("Unknown format: {}".format(format))
    for spectra in gen:
        yield spectra

def fromBruker(file, remove_filter=True, read_pdata=True):
    try:
        dic, data = bruker.read(file)
    except IOError:
        return None
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
