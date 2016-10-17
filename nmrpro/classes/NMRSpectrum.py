import numpy as np
from nmrglue.process.proc_base import ifft, fft, tp_hyper, c2ri
from nmrglue.fileio.fileiobase import unit_conversion
from collections import OrderedDict
from nmrpro.utils import num_unit
from nmrpro.workflows import Workflow, WorkflowStep
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
        
        if copy or (self.nbytes != data.nbytes):#TODO: or (self.shape != data.shape):
            return DataUdic(data, udic) #TODO: return same subclass
        
        if flag == 'nohyper':
            self = self.transpose()
        else:
            try:
                self.data = data.data
                self.dtype = data.dtype
                self.shape = data.shape
            except AttributeError:
                return DataUdic(data, udic)
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
    def __new__(cls, input_array, udic, parent=None, uc=None):
        if input_array.ndim == 1:
            cls = NMRSpectrum1D
        elif input_array.ndim == 2:
            cls = NMRSpectrum2D
        obj = np.asarray(input_array).view(cls)

        
        if parent is None:
            history = Workflow()
            original = DataUdic(input_array, udic)
            flags = {}
        else:
            history = parent.history
            original = parent.original
            flags = parent.spec_flags
            if uc is None: uc = parent.uc
        
        # add the new attribute to the created instance
        if uc is None:
            uc = [unit_conversion(udic[i]['size'],
                                    udic[i]['complex'],
                                    udic[i]['sw'],
                                    udic[i]['obs'],
                                    udic[i]['car'])
                for i in range(0, udic['ndim'])]

        
        obj.udic = udic
        obj.uc = uc
        obj.history = history
        obj.original = original
        obj.spec_flags = flags
        return obj

    def __array_finalize__(self, obj):
        if obj is None:
            return
        self.udic = getattr(obj, 'udic', None)
        self.uc = getattr(obj, 'uc', None)
        self.history = getattr(obj, 'history', None)
        self.original = getattr(obj, 'original', None)
        self.spec_flags = getattr(obj, 'spec_flags', {})

    ################# Slicing with units  #####################
    def __getitem__(self, idx):
        if isinstance(idx, tuple):
            idx = tuple( self._convert_unit(element, dim) for dim, element in enumerate(idx) )
        else:
            idx = self._convert_unit(idx)
        
        return super(NMRSpectrum, self).__getitem__(idx)
    
    def _convert_slice(self, s, dim=0):
        start = self._convert_unit(s.start)
        stop = self._convert_unit(s.stop)
        if isinstance(s.step, basestring):
            step = self.interval(s.step)
        else : step = s.step
    
        return slice(start, stop, step)
    
    def _convert_unit(self, idx, dim=0):
        if isinstance(idx, slice):
            return self._convert_slice(idx)
    
        if isinstance(idx, basestring):
            #TODO: testing on 2D dimensions, negative indices, very small steps
            # testing if/when uc should be updated, esp. in states encoding.
            number, unit = num_unit(idx)
            try: return self.uc[dim].i(number, unit)
            except ValueError: 
                raise ValueError('Incompatible unit %s. Possible units: ppm, ms, hz' %unit)
        else:
            return idx
    
    def interval(self, step):
        step_unit = num_unit(step)[1]
        return self._convert_unit(step) - self._convert_unit('0'+step_unit)
    
    ################# Data processing  #####################
    def tp(self, copy=True, flag='auto'):
        _ret = super(NMRSpectrum, self).tp(copy, flag)
        if isinstance(_ret, DataUdic):
            return NMRSpectrum(_ret, _ret.udic, self)
        
        return _ret
    
    def setData(self, input_array):
        if hasattr(input_array, 'udic'):
            udic = input_array.udic
        else:
            udic = self.udic
            
        if self.nbytes != input_array.nbytes:# TODO: or self.shape != input_array.shape:
            return NMRSpectrum(input_array, udic, self)
        
        
        self.data = input_array.data
        self.dtype = input_array.dtype
        self.shape = input_array.shape
        self.udic = udic

        return self

    def fapply(self, fun, message):
        step = WorkflowStep(fun)
        step.operation_name = message
        
        self.history.append(step)
        return self.setData(fun(self))

    def fapplyAtIndex(self, fun, message, idx):
        step = WorkflowStep(fun)
        step.operation_name = message
        
        self.history.append(step, order=idx)
        return self.update_data()

    def fapplyAfter(self, fun, message, element):
        step = WorkflowStep(fun)
        step.operation_name = message
        step.set_order(after=element)
        self.history.append(step)
        return self.update_data()

    def fapplyBefore(self, fun, message, element):
        step = WorkflowStep(fun)
        step.operation_name = message
        step.set_order(before=element)
        self.history.append(step)
        return self.update_data()

    def fapplyAt(self, fun, message, element=None):
        if element is None:
            element = message

        step = WorkflowStep(fun)
        step.operation_name = message
        step.set_order(replaces=element)
        self.history.append(step)
        return self.update_data()

    
    def update_data(self):
        return self.history.execute(self)
    
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
        #

        #def __array_wrap__(self, obj):
        #    super(NMRSpectrum1D, self).__array_wrap__(obj)


class NMRSpectrum2D(NMRSpectrum):
    def __array_finalize__(self, obj):
        super(NMRSpectrum2D, self).__array_finalize__(obj)
        #
        
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

        