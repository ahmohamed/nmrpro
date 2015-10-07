import numpy as np
from nmrglue.process.proc_base import ifft, fft, rev, cs, tp_hyper, c2ri
import nmrglue.process.pipe_proc as pp
from nmrglue.fileio import bruker, pipe
from nmrglue.fileio.fileiobase import unit_conversion, uc_from_udic
from collections import OrderedDict
from ..utils import make_uc_pipe, num_unit
from ..NMRFileManager import find_pdata
from copy import deepcopy

class DataUdic(np.ndarray):
    def __new__(cls, data, udic):
        obj = np.asarray(data).view(cls)
        obj.udic = udic
        return obj
        
    def __array_finalize__(self, obj):
        self.udic = getattr(obj, 'udic', None)
        self.history = getattr(obj, 'history', None)
    
    def __array_wrap__(self, obj):
        if obj.shape == ():
            return obj[()]    # if ufunc output is scalar, return it
        else:
            return np.ndarray.__array_wrap__(self, obj)
    
    def tp(self, copy=True, flag='auto'):
        if self.udic['ndim'] < 2: return self
        
        if flag != 'nohyper':
            if (self.udic[0]['complex'] and self.udic[1]['complex']) or\
                flag == 'hyper':
                data = np.array(tp_hyper(self), dtype="complex64")
            else:
                data = self.transpose()
                if self.udic[0]['complex']:
                    data = np.array(c2ri(data), dtype="complex64")
        
        if flag == 'nohyper':                
            data = self.transpose()
        
        # copy the udic and reverse the dimensions
        udic = {k:v for k,v in self.udic.items()}
        temp = udic[0]
        udic[0] = udic[1]
        udic[1] = temp
        
        if copy or (self.nbytes != data.nbytes) or (self.shape != data.shape):
            return DataUdic(data, udic)
        
        if flag == 'nohyper':
            self = self.transpose()
        else:
            self.shape = data.shape
            self.data = data
        self.udic = udic
        
        # TODO: update udic[size]. add 'transposed' to udic?
        return self
    
    def real_part(self):
        return self.di().tp().di().tp()
    
    def di(self):
        dim = self.udic['ndim'] -1
        udic_copy = self.copy_udic()
        udic_copy[dim]['complex'] = False
        return DataUdic(self.real, udic_copy)
    
    def copy_udic(self):
        return deepcopy(self.udic)
    


class NMRSpectrum(DataUdic):
    @classmethod
    def fromFile(cls, *args, **kwargs):
        from ..readers import fromFile
        return fromFile(*args, **kwargs)
        
    @classmethod
    def fromBruker(cls, *args, **kwargs):
        from ..readers import fromBruker
        return fromBruker(*args, **kwargs)

    @classmethod
    def fromPipe(cls, *args, **kwargs):
        from ..readers import fromPipe
        return fromPipe(*args, **kwargs)

    def __new__(cls, input_array, udic, parent=None, uc=None):
        if input_array.ndim == 1:
            cls = NMRSpectrum1D
        elif input_array.ndim == 2:
            cls = NMRSpectrum2D
        obj = np.asarray(input_array).view(cls)

        
        if parent is None:
            history = OrderedDict()
            history['original'] = lambda s: s
            original = DataUdic(input_array, udic)
        else:
            history = parent.history
            original = parent.original
            if uc is None: uc = parent.uc
        
        # add the new attribute to the created instance
        print(udic['ndim'])
        if uc is None:
            uc = [unit_conversion(udic[i]['size'],
                                    udic[i]['complex'],
                                    udic[i]['sw'],
                                    udic[i]['obs'],
                                    udic[i]['car'])
                for i in range(0, udic['ndim'])]

        # if type(uc) is list and len(uc) == 1:
        #     uc = uc[0]

        
        obj.udic = udic
        obj.uc = uc
        obj.history = history
        obj.original = original
        return obj

    def __array_finalize__(self, obj):
        if obj is None:
            return
        self.udic = getattr(obj, 'udic', None)
        self.uc = getattr(obj, 'uc', None)
        self.history = getattr(obj, 'history', None)
        self.original = getattr(obj, 'original', None)

    
    def __getitem__(self, idx):
        if isinstance(idx, tuple):
            idx = tuple( self._convert_unit(element, i) for i, element in enumerate(idx) )
        else:
            idx = self._convert_unit(idx)
        
        return super(NMRSpectrum, self).__getitem__(idx)
    
    def _convert_slice(self, s, dim=0):
        start = self._convert_unit(s.start)
        stop = self._convert_unit(s.stop)
        if isinstance(s.step, basestring):
            step_unit = num_unit(s.step)[1]
            step = self._convert_unit(s.step) - self._convert_unit('0'+step_unit)
        else : step = s.step
    
        return slice(start, stop, step)
    
    def _convert_unit(self, idx, dim=0):
        if isinstance(idx, slice):
            return self._convert_slice(idx)
    
        if isinstance(idx, basestring):
            #TODO: testing on 2D dimensions, negative indices, very small steps
            # testing if/when uc should be updated, esp. in states encoding.
            return self.uc[dim].i(*num_unit(idx))
        else:
            return idx
    
    ################# Data processing  #####################
    def setData(self, input_array):
        if hasattr(input_array, 'udic'):
            udic = input_array.udic
        else:
            udic = self.udic
            
        if self.nbytes != input_array.nbytes or self.shape != input_array.shape:
            return NMRSpectrum(input_array, udic, self)

        self.data = input_array.data
        self.dtype = input_array.dtype
        self.udic = udic

        return self

    def fapply(self, fun, message):
        self.history[message] = fun
        return self.setData(fun(self))

    def fapplyAtIndex(self, fun, message, idx):
        hist_keys = self.history.keys()
        hist_keys.insert(idx, message)

        hist_funcs = self.history.values()
        hist_funcs.insert(idx, fun)
        self.history = OrderedDict(zip(hist_keys, hist_funcs))
        return self.update_data()

    def fapplyAfter(self, fun, message, element):
        try:
            idx = self.history.keys().index(element) + 1
        except ValueError:
            return self.fapply(fun, message)

        return self.fapplyAtIndex(fun, message, idx)

    def fapplyBefore(self, fun, message, element):
        try:
            idx = self.history.keys().index(element)
        except ValueError:
            return self.fapply(fun, message)

        return self.fapplyAtIndex(fun, message, idx)

    def fapplyAt(self, fun, message, element=None):
        if element is None:
            element = message
        try:
            idx = self.history.keys().index(element)
        except ValueError:
            return self.fapply(fun, message)

        self.history[message] = fun
        return self.update_data()

    
    def update_data(self):
        return self.setData(reduce(lambda x, y: y(x), self.history.values(), self.original))
    
    def getSpectrumAt(self, element, include=False):
        idx = self.history.keys().index(element) + include # if true, include evaluate to 1.
        fn_list = self.history.values()[0:idx]
        return reduce(lambda x, y: y(x), fn_list, self.original)
        
    def original_data(self):
        return self.original

    def time_domain(self):
        if self.udic[0]['freq']:
            return ifft(self)
        else:
            return self

    def freq_domain(self):
        if self.udic[0]['freq']:
            return self
        else:
            return fft(self)
    
    def is_time_domain(self):
        return [self.udic[i]['time'] for i in range(0, self.udic['ndim'])]
    
class NMRSpectrum1D(NMRSpectrum):
    def __array_finalize__(self, obj):
        super(NMRSpectrum1D, self).__array_finalize__(obj)
        #print("final1d")

        #def __array_wrap__(self, obj):
        #    super(NMRSpectrum1D, self).__array_wrap__(obj)


class NMRSpectrum2D(NMRSpectrum):
    def __array_finalize__(self, obj):
        super(NMRSpectrum2D, self).__array_finalize__(obj)
        #print("final2d", getattr(obj, 'uc', None))
        
    # def tp(self, copy=True):
    #     if self.udic[0]['complex'] and self.udic[1]['complex']:
    #         data = np.array(tp_hyper(self), dtype="complex64") #tp_hyper(self)
    #     elif self.udic[1]['complex']:
    #         data = np.array(p.c2ri(data), dtype="complex64")
    #     else:
    #         data = self.transpose()
    #
    #     udic = udic = {k:v for k,v in self.udic.items()}
    #     temp = udic[0]
    #     udic[0] = udic[1]
    #     udic[1] = temp
    #
    #     if copy:
    #         return DataUdic(data, udic)
    #
    #     self.shape = data.shape
    #     self.data = data
    #     self.udic = udic
    #
    #     # TODO: update udic[size]. add 'transposed' to udic?
    #     return self

class NMRDataset():
    def __init__(self, nd, *specs):
        self.nd = nd
        self.specList = list()
        for s in specs:
            self.specList.append(s)

    def __len__(self):
        return len(self.specList)
        
    def __getitem__(self, key):
        return self.specList[key]
        
    
    def __setitem__(self, key, value):
        self.specList[key] = value

    def append(self, s):
        self.specList.append(s)
    
    def pop(self, key):
        return self.specList.pop(key)

class SpecFeature():
    def __init__(self, data, parentSpec):
        self.data = data
        self.spec = parentSpec
        
class SpecLike():
    def __init__(self, data, parentSpec):
        self.data = data
        self.spec = parentSpec

        