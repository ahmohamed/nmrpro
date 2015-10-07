import unittest
import nmrglue as ng
from ...classes.NMRSpectrum import NMRSpectrum
from .fft import webFFT
import numpy.testing as ts
from numpy import array

class fft_1DTest(unittest.TestCase):
    def setUp(self):
        dic, data = ng.bruker.read("./test_files/Bruker_1D/", read_pulseprogram=False)
        self.dic = dic
        self.data = data
        self.filename = "./test_files/Bruker_1D/"
        #self.string = 'Hello World'
    
    def test_fft_norm(self):
        spec = NMRSpectrum.fromBruker(self.filename, False, False)
        spec = webFFT(spec, {'a':'norm'})
        
        ts.assert_array_equal(spec, ng.process.proc_base.fft_norm(self.data), 'FFT_norm failed')
        self.assertEqual(spec.udic[0]['freq'], True, 'Spec udic not modified to freq=True')

    def test_fft_pos(self):
        spec = NMRSpectrum.fromBruker(self.filename, False, False)
        spec = webFFT(spec, {'a':'pos'})
        
        ts.assert_array_equal(spec, ng.process.proc_base.fft_positive(self.data), 'FFT_positive failed')
        self.assertEqual(spec.udic[0]['freq'], True, 'Spec udic not modified to freq=True')
        
    def test_fft_object_overwrite(self):
        spec = NMRSpectrum.fromBruker(self.filename, False, False)
        webFFT(spec, {'a':'fft'})
        
        ts.assert_array_equal(spec, ng.process.proc_base.fft(self.data), 'Simple FFT falied')
        self.assertEqual(spec.udic[0]['freq'], True, 'Spec udic not modified to freq=True')

    def test_fft_multiple_fft(self):
        spec = NMRSpectrum.fromBruker(self.filename, False, False)
        webFFT(spec, {})
        webFFT(spec, {'a':'norm'})
        
        ts.assert_array_equal(spec, ng.process.proc_base.fft_norm(self.data), 'FFT overwriting failed')
        self.assertEqual(spec.udic[0]['freq'], True, 'Spec udic not modified to freq=True')
        
                
class fft_2DTest(unittest.TestCase):
    def setUp(self):
        dic, data = ng.pipe.read("./test_files/bmse000281_hsqc.fid")        
        self.dic = dic
        self.data = data
        self.filename = "./test_files/bmse000281_hsqc.fid"
        
    def test_fft_pipe(self):
        dic, data = self.dic, self.data
        spec2d = NMRSpectrum.fromPipe(self.filename)
        # testing hypercomplex
        fn = "FDF" + str(int(dic["FDDIMORDER"][0]))
        fn2 = "FDF" + str(int(dic["FDDIMORDER"][1]))
        self.assertEqual((dic[fn + "QUADFLAG"] != 1) and \
                         (dic[fn2 + "QUADFLAG"] != 1), True,
                         'QUADFLAGs Error: data is not complex')
        
        # testing hypercomplex transpose
        ts.assert_array_equal(ng.pipe_proc.tp(dic, data,auto=True)[1],
                              array(ng.proc_base.tp_hyper(data), dtype="complex64"))
        
        dic2, data2 = ng.pipe_proc.tp(dic, data, auto=True)

        # test class implementation of tp with pipe_proc
        ts.assert_array_equal(data2, spec2d.tp(),
                              'class implementation of tp not matching pipe.')        
        
        # test double transpose
        ts.assert_array_equal(ng.pipe_proc.tp(dic2, data2,auto=True)[1], data,
                              'Pipe tp: double transpose not giving the original data')
        
        
        # test double transpose with class implementation
        ts.assert_array_equal(spec2d.tp().tp(), spec2d,
                              'Double tp with class implementation not giving '
                              'the original data')

        # test pipe_ft
        ts.assert_array_equal(ng.pipe_proc.ft(dic, data)[1], 
                              ng.proc_base.fft_positive(data),
                              'pipe_proc.ft not equal to fft_positive')

        
        # 2D FFT using pipe_proc functions
        dic3, data3 = ng.pipe_proc.ft(dic, data)
        dic3, data3 = ng.pipe_proc.tp(dic3, data3, auto=True)
        dic3, data3 = ng.pipe_proc.ft(dic3, data3)
        dic3, data3 = ng.pipe_proc.tp(dic3, data3, auto=True)
        
        # test auto class implementation
        ffted = webFFT(spec2d,{})
        ts.assert_equal(data3, ffted, '2D FFT doesnt match pipe_proc.ft')
        
        self.assertEqual((ffted.udic[0]['time'] or ffted.udic[1]['time']),
                         False, 'udic time paramter not set to False')
        self.assertEqual((ffted.udic[0]['freq'] and ffted.udic[1]['freq']),
                         True, 'udic freq paramter not set to True')
