import unittest
import nmrglue as ng
from nmrpro.readers import fromBruker, fromPipe
from nmrpro.classes.NMRSpectrum import NMRSpectrum
from nmrpro.plugins.PluginMount import JSCommand
from .fft import fft1d
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
        spec = fromBruker(self.filename, False, False)
        spec = fft1d(spec, 'norm')
        
        ts.assert_array_equal(spec, ng.process.proc_base.fft_norm(self.data), 'FFT_norm failed')
        self.assertEqual(spec.udic[0]['freq'], True, 'Spec udic not modified to freq=True')

    def test_fft_pos(self):
        spec = fromBruker(self.filename, False, False)
        spec = fft1d(spec, 'pos')
        
        ts.assert_array_equal(spec, ng.process.proc_base.fft_positive(self.data), 'FFT_positive failed')
        self.assertEqual(spec.udic[0]['freq'], True, 'Spec udic not modified to freq=True')
    
    @unittest.expectedFailure    
    def test_fft_object_overwrite(self):
        spec = fromBruker(self.filename, False, False)
        fft1d(spec, 'fft')
        
        ts.assert_array_equal(spec, ng.process.proc_base.fft(self.data), 'Simple FFT falied')
        self.assertEqual(spec.udic[0]['freq'], True, 'Spec udic not modified to freq=True')

    def test_fft_repeatable_fft(self):
        spec = fromBruker(self.filename, False, False)
        spec = fft1d(spec, 'norm')
        spec = fft1d(spec, 'norm')
        
        ts.assert_array_equal(spec, ng.process.proc_base.fft_norm(self.data), 'FFT overwriting failed')
        self.assertEqual(spec.udic[0]['freq'], True, 'Spec udic not modified to freq=True')

    def test_fft_multiple_fft(self):
        spec = fromBruker(self.filename, False, False)
        spec = fft1d(spec)
        spec = fft1d(spec, 'norm')
        
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
        spec2d = fromPipe(self.filename)
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
        ffted = fft1d(spec2d)
        ts.assert_equal(data3, ffted, '2D FFT doesnt match pipe_proc.ft')
        
        self.assertEqual((ffted.udic[0]['time'] or ffted.udic[1]['time']),
                         False, 'udic time paramter not set to False')
        self.assertEqual((ffted.udic[0]['freq'] and ffted.udic[1]['freq']),
                         True, 'udic freq paramter not set to True')


class fftCommandTest(unittest.TestCase):
    def setUp(self):
        js_class = [p for p in JSCommand.plugins if p.menu_path[-1] == 'FFT'][0]
        self.command = js_class.fun
        self.d1_file = "./test_files/Bruker_1D/"
        self.d2_file = "./test_files/bmse000281_hsqc.fid"
            
    def test_fft_command_1d(self):
        spec = fromBruker(self.d1_file, False, False)
        spec = self.command(spec, {})
        
        dic, data = ng.bruker.read(self.d1_file, read_pulseprogram=False)
        ts.assert_array_equal(spec, ng.process.proc_base.fft_positive(data), '1D FFT command failed')
        self.assertEqual(spec.udic[0]['freq'], True, 'Spec udic not modified to freq=True')
        
        spec = self.command(spec, {})
        ts.assert_array_equal(spec, ng.process.proc_base.fft_positive(data), 'Repetitive 1D FFT command failed')
    
    def test_fft_command_2d(self):
        spec = fromPipe(self.d2_file)
        spec = self.command(spec, {})
        
        dic, data = ng.pipe.read(self.d2_file)
        
        # 2D FFT using pipe_proc functions
        dic3, data3 = ng.pipe_proc.ft(dic, data)
        dic3, data3 = ng.pipe_proc.tp(dic3, data3, auto=True)
        dic3, data3 = ng.pipe_proc.ft(dic3, data3)
        dic3, data3 = ng.pipe_proc.tp(dic3, data3, auto=True)
        
        ts.assert_equal(data3, spec, '2D FFT command doesnt match pipe_proc.ft')
        
        self.assertEqual((spec.udic[0]['time'] or spec.udic[1]['time']),
                         False, 'udic time paramter not set to False')
        self.assertEqual((spec.udic[0]['freq'] and spec.udic[1]['freq']),
                         True, 'udic freq paramter not set to True')
        
        
        spec = self.command(spec, {})
        ts.assert_equal(data3, spec, 'Rpetitive 2D FFT command doesnt match pipe_proc.ft')
        
        self.assertEqual((spec.udic[0]['time'] or spec.udic[1]['time']),
                         False, 'udic time paramter not set to False')
        self.assertEqual((spec.udic[0]['freq'] and spec.udic[1]['freq']),
                         True, 'udic freq paramter not set to True')
    