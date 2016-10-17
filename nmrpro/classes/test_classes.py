import unittest
from nmrpro.readers import fromBruker, fromPipe, fromFile
from .NMRSpectrum import NMRSpectrum, NMRDataset
import numpy.testing as ts
import nmrglue as ng

class SpectrumTest(unittest.TestCase):
    def setUp(self):
        spec1d = fromFile('./test_files/Bruker_1D/', 'Bruker')
        self.spec1d = spec1d
        self.fid_file = './test_files/bmse000281_hsqc.fid'

    def test_unitconversion(self):
        '''Testing unit conversion in NMRSpectrum'''
        wrong = ['aa', '-.1p']
        right = ['0.1', '.1ppm', '-1000ms', '-.1HZ']
        # TODO: complete testing. 2D cases. step cases
        
    
class DatasetTest(unittest.TestCase):
    def setUp(self):
        spec1d = fromFile('./test_files/Bruker_1D/', 'Bruker')
        ds = NMRDataset(1, spec1d, spec1d, spec1d)
        self.ds = ds
        self.spec1d = spec1d
        self.fid_file = './test_files/bmse000281_hsqc.fid'

    def test_Dataset_init_iter(self):
        ds = self.ds
        assert(len(ds) == 3)

        s_list = [s for s in ds]
        assert(len(s_list) == 3)
        assert(type(s_list)== list)

    def test_Dataset_get_setitem(self):
        ds = self.ds
        ts.assert_array_equal(ds[0], ds.specList[0])

        # test_Dataset_setitem
        s_copy = self.spec1d.copy()
        s_copy[:] = 0
        ds[2] = s_copy
        ts.assert_array_equal(ds[2], s_copy)

    def test_Dataset_append_pop(self):
        ds = self.ds
        s_copy = self.spec1d.copy()
        s_copy[:] = 0
    
        ds.append(s_copy)
        assert(len(ds) == 4)
        ts.assert_array_equal(ds[3], s_copy)

        ts.assert_array_equal(ds.pop(2), self.spec1d)
        assert(len(ds) == 3)
        ts.assert_array_equal(ds[2], s_copy)
        
    def test_di(self):
        dic, data = ng.pipe.read(self.fid_file)
        spec2d = fromPipe(self.fid_file)
        
        
        self.assertEqual(data.dtype, spec2d.dtype, 'Initial dtype dont match')
        self.assertEqual(data.shape, spec2d.shape, 'Initial data shapes dont match')
        for i in range(0,spec2d.ndim):
            spec2d = spec2d.di().tp()
            dic, data = ng.pipe_proc.di(dic, data)
            dic, data = ng.pipe_proc.tp(dic, data, auto=True)
            self.assertEqual(data.dtype, spec2d.dtype, 'dtype dont match for dimension '+str(i))
            self.assertEqual(data.shape, spec2d.shape, 'data shapes dont match for dimension '+str(i))
            