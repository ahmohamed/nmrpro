import unittest
from nmrglue.process.proc_base import zf_size, fft
from nmrglue.fileio.bruker import read
import nmrglue as ng
from nmrpro.readers import fromBruker, fromPipe
from nmrpro.classes.NMRSpectrum import NMRSpectrum
from .zf import zf1d, zf2d
from nmrpro.plugins.FFT.fft import fft1d
import numpy.testing as ts

class zf_1DTest(unittest.TestCase):
    def setUp(self):
        dic, data = read("./test_files/Bruker_1D/", read_pulseprogram=False)
        self.dic = dic
        self.data = data
        self.filename = "./test_files/Bruker_1D/"
        #self.string = 'Hello World'
    
    def test_zf(self):
        spec = fromBruker(self.filename, False, False)
        spec = zf1d(spec, size = 2**15)
        
        ts.assert_array_equal(spec, zf_size(self.data, 2**15), 'Simple Zero filling falied (see zf_size)')
        self.assertEqual(spec.shape[-1], 2**15, 'Spec size is not correct')
        self.assertEqual("ZF" in spec.history._stepnames, True, 'ZF not added to Spec history')
        self.assertEqual(spec.udic[0]['size'], 2**15, 'udic size not set correctly')

    @unittest.expectedFailure
    def test_zf_object_overwrite(self):
        spec = fromBruker(self.filename, False, False)
        zf1d(spec, size = 2**15)
        
        ts.assert_array_equal(spec, zf_size(self.data, 2**15), 'Simple Zero filling falied (see zf_size)')
        self.assertEqual(spec.shape[-1], 2**15, 'Spec size is not correct')
        self.assertEqual("ZF" in spec.history._stepnames, True, 'ZF not added to Spec history')
        self.assertEqual(spec.udic[0]['size'], 2**15, 'udic size not set correctly')
        

    def test_zf_with_fft(self):
        spec = fromBruker(self.filename, False, False)
        spec = fft1d(spec, 'fft')
        spec = zf1d(spec, size = 2**15)
        
        test_data = fft(zf_size(self.data, 2**15))
        self.assertEqual(spec.shape[-1], 2**15, 'Spec size is not correct')
        self.assertEqual("ZF" in spec.history._stepnames, True, 'ZF not added to Spec history')
        self.assertEqual(spec.history._stepnames, ['ZF','FFT'], 'Spec history not in the correct order (See fapplyBefore)')
        ts.assert_array_equal(spec, test_data, 'Simple Zero filling falied (see zf_size)')
        self.assertEqual(spec.udic[0]['size'], 2**15, 'udic size not set correctly')        
                

class zf_2DTest(unittest.TestCase):
    def setUp(self):
        dic, data = ng.pipe.read("./test_files/bmse000281_hsqc.fid")        
        self.dic = dic
        self.data = data
        self.filename = "./test_files/bmse000281_hsqc.fid"

    def test_zf_pipe(self):
        dic, data = self.dic, self.data
        spec2d = fromPipe(self.filename)
        
        def zf2d_pipe(dic, data, size, size2):
            dic2, data2 = ng.pipe_proc.zf(dic,data, size=size)
            dic2, data2 = ng.pipe_proc.tp(dic2, data2, nohyper=True)
            dic2, data2 = ng.pipe_proc.zf(dic2, data2, size=size2)
            dic2, data2 = ng.pipe_proc.tp(dic2, data2, nohyper=True)    
            return dic2, data2
            
        pipe_zf = zf2d_pipe(dic, data, 2048, 512)[1]
        spec2d = zf2d(spec2d, size = 2048, size2=512)
        self.assertEqual(spec2d.shape, (512, 2048), 'Zero filled 2D spectrum has incorrect shape')
        ts.assert_array_equal(spec2d, pipe_zf, 'Zero filled 2D spectrum not equal to pipe_proc spectrum')
    
    def test_zf_auto(self):
        dic, data = self.dic, self.data
        spec2d = fromPipe(self.filename)
        
        spec2d = zf2d(spec2d)
        self.assertEqual(spec2d.shape, (512, 1900), 'Incorrect size in zero filling with size=auto')