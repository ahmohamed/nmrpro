import unittest
import nmrglue.process.proc_base as ngp
import nmrglue.process.pipe_proc as pipep
from nmrglue.fileio.bruker import read,guess_udic
import nmrglue.fileio.pipe as pipe
from nmrglue.fileio.convert import converter
from nmrpro.readers import fromBruker, fromPipe
from nmrpro.classes.NMRSpectrum import NMRSpectrum
from nmrpro.exceptions import NMRShapeError
from nmrpro.plugins.ZF.zf import zf1d
from nmrpro.plugins.FFT.fft import fft1d
from .apod import *
import numpy.testing as ts

#TODO: apod_2Dtest

class apod_1DTest(unittest.TestCase):
    def setUp(self):
        dic, data = read("./test_files/Bruker_1D/", read_pulseprogram=False)
        self.dic = dic
        self.data = data
        self.filename = "./test_files/Bruker_1D/"
    
    def test_apod(self):
        spec = fromBruker(self.filename, False, False)
        spec = apod(spec, w=lambda s: EM(s, 0.))
        
        ts.assert_array_equal(spec, ngp.em(self.data), 'Simple EM apodization failed')
        self.assertEqual("apodization" in spec.history._stepnames, True, 'Apodization not added to Spec history %s' %str(spec.history._stepnames))

    def test_apod_multiple(self):
        spec = fromBruker(self.filename, False, False)
        spec = apod(spec, w=lambda s: EM(s, 0.), w2=lambda s: GM(s))
        
        test_data = ngp.em(self.data)
        test_data = ngp.gm(test_data)
        
        ts.assert_array_equal(spec, test_data, 'Multiple apodization (EM + GM) failed')
        self.assertEqual("apodization" in spec.history._stepnames, True, 'Apodization not added to Spec history')
        
    # def test_apod_object_overwrite(self):
    #     spec = fromBruker(self.filename, False, False)
    #     webApod(spec, {'em':'True', 'em_lb':'0'})
    #
    #     ts.assert_array_equal(spec, ngp.em(self.data), 'Simple EM apodization failed')
    #     self.assertEqual("apod" in spec.history._stepnames, True, 'Apodization not added to Spec history')

    def test_apod_with_zf_fft(self):
        spec = fromBruker(self.filename, False, False)
        spec = fft1d(spec, 'fft')
        spec = zf1d(spec, size=2**15)
        spec = apod(spec, w=lambda s: EM(s, 0.))

        test_data = ngp.fft(ngp.zf_size( ngp.em(self.data) , 2**15))
        self.assertEqual(spec.shape[-1], 2**15, 'Spec size is not correct')
        ts.assert_array_equal(spec, test_data, 'Apodization with zero filling and FFT failed.')
        self.assertEqual("apodization" in spec.history._stepnames, True, 'Apodization not added to Spec history')
        self.assertEqual(spec.history._stepnames, ['apodization','ZF','FFT'], 'Spec history not in the correct order (See fapplyBefore)')
    
    def test_apod_with_fft(self):
        spec = fromBruker(self.filename, False, False)
        spec = fft1d(spec, 'fft')
        spec = apod(spec, w=lambda s: EM(s, 0.))
        
        test_data = ngp.fft( ngp.em(self.data) )
        ts.assert_array_equal(spec, test_data, 'Apodization with zero filling and FFT failed.')
        self.assertEqual("apodization" in spec.history._stepnames, True, 'Apodization not added to Spec history')
        self.assertEqual(spec.history._stepnames, ['apodization', 'FFT'], 'Spec history not in the correct order (See fapplyBefore)')
    
    
    ##### Test nmrglue functions using a NMRPipe file ########    
    def test_apod_em(self):
        spec = fromBruker(self.filename, False, False)
        spec = apod(spec, w=lambda s: EM(s))
        C = converter()
        u = guess_udic(self.dic,self.data)
        C.from_bruker(self.dic, self.data, u)
        
        pipe_dic, pipe_data = C.to_pipe()
        test_data = pipep.em(pipe_dic, pipe_data, lb=0.2)[1]        
        ts.assert_allclose(spec, test_data, 1e-7,1e-3, 'EM apodization not equal to NMRPipe processed one.')
        
                    
    def test_apod_gm(self):
        spec = fromBruker(self.filename, False, False)
        spec = apod(spec, w=lambda s: GM(s, 1, 10, 5))
        C = converter()
        u = guess_udic(self.dic,self.data)
        C.from_bruker(self.dic, self.data, u)
        
        pipe_dic, pipe_data = C.to_pipe()
        test_data = pipep.gm(pipe_dic, pipe_data, g1=1, g2=10, g3=5)[1]        
        ts.assert_allclose(spec, test_data, 1e-7,1e-3, 'GM apodization not equal to NMRPipe processed one.')

    def test_apod_gmb(self):
        spec = fromBruker(self.filename, False, False)
        spec = apod(spec, w=lambda s: GMB(s, 2, 0.5))
        C = converter()
        u = guess_udic(self.dic,self.data)
        C.from_bruker(self.dic, self.data, u)
        
        pipe_dic, pipe_data = C.to_pipe()
        test_data = pipep.gmb(pipe_dic, pipe_data, lb=2, gb=0.5)[1]
        ts.assert_allclose(spec, test_data, 1e-7,1e-3, 'GBM apodization not equal to NMRPipe processed one.')
        
        
    def test_apod_jmod(self):
        spec = fromBruker(self.filename, False, False)
        spec = apod(spec, w=lambda s: JMOD(s, 0.5, 5, 1))
        C = converter()
        u = guess_udic(self.dic,self.data)
        C.from_bruker(self.dic, self.data, u)
        
        pipe_dic, pipe_data = C.to_pipe()
        test_data = pipep.jmod(pipe_dic, pipe_data, off=0.5, j=5, lb=1)[1]        
        ts.assert_allclose(spec, test_data, 1e-7,1e-3, 'JMOD apodization not equal to NMRPipe processed one.')
        
        
    def test_apod_sp(self):
        spec = fromBruker(self.filename, False, False)
        spec = apod(spec, w=lambda s: SP(s, off=0.5, power=2))
        C = converter()
        u = guess_udic(self.dic,self.data)
        C.from_bruker(self.dic, self.data, u)
        
        pipe_dic, pipe_data = C.to_pipe()
        test_data = pipep.sp(pipe_dic, pipe_data, off=0.5, pow=2)[1]        
        ts.assert_allclose(spec, test_data, 1e-7,1e-3, 'SP apodization not equal to NMRPipe processed one.')
        
        
    def test_apod_tm(self):
        spec = fromBruker(self.filename, False, False)
        # t1 < 1 results in dimension reduction of the apodization vector
        with self.assertRaises(NMRShapeError):
            apod(spec, w=lambda s: TM(s, 0.5, 10000))

        spec = fromBruker(self.filename, False, False)
        spec = apod(spec, w=lambda s: TM(s, 5000, 10000))
        C = converter()
        u = guess_udic(self.dic,self.data)
        C.from_bruker(self.dic, self.data, u)
        
        pipe_dic, pipe_data = C.to_pipe()
        test_data = pipep.tm(pipe_dic, pipe_data, t1=5000, t2=10000)[1]
        ts.assert_allclose(spec, test_data, 1e-7,1e-3, 'TM apodization not equal to NMRPipe processed one.')
        
        
    def test_apod_tri(self):
        spec = fromBruker(self.filename, False, False)        
        # Loc < 1 results in dimension reduction of the apodization vector
        with self.assertRaises(NMRShapeError):
            apod(spec, w=lambda s: TRI(s, 0.5, 0.7, 0.5))
        
        spec = fromBruker(self.filename, False, False)
        spec = apod(spec, w=lambda s: TRI(s, 5000, 0.7, 0.5))
        C = converter()
        u = guess_udic(self.dic,self.data)
        C.from_bruker(self.dic, self.data, u)
        
        pipe_dic, pipe_data = C.to_pipe()
        test_data = pipep.tri(pipe_dic, pipe_data, loc=5000, lHi=0.7, rHi=0.5)[1]
        ts.assert_allclose(spec, test_data, 1e-7,1e-3, 'TRI apodization not equal to NMRPipe processed one.')
        

class apod_2DTest(unittest.TestCase):
    def setUp(self):
        dic, data = pipe.read("./test_files/bmse000281_hsqc.fid")        
        self.dic = dic
        self.data = data
        self.filename = "./test_files/bmse000281_hsqc.fid"
    
    
    def test_apod_pipe(self):
        dic, data = self.dic, self.data
        spec2d = fromPipe(self.filename)
        
        
        # 2D FFT using pipe_proc functions
        dic3, data3 = pipep.em(dic, data, 0.2)
        dic3, data3 = pipep.tp(dic3, data3, auto=True)
        dic3, data3 = pipep.em(dic3, data3, 0.2)
        dic3, data3 = pipep.tp(dic3, data3, auto=True)
        
        # test auto class implementation
        apoded = apod(spec2d, w=lambda s: EM(s))
        ts.assert_equal(data3, apoded, '2D Apodized spectrum doesnt match pipe_proc.em')
    
    def test_apod_unity(self):
        dic, data = self.dic, self.data
        spec2d = fromPipe(self.filename)
        
        # test auto class implementation
        apoded = apod(spec2d)
        ts.assert_equal(data, apoded, '2D Apodization unity failed')
    
    
    
    def test_unity_with_fft(self):
        ''' This tests the not only that apodization of no arguments has no effect
            on the spectrum, but also it makes sure the 'no_transpose' flag is
            correctly set and reset.
        '''
        spec2d = fromPipe(self.filename)
        apoded_2d = apod(spec2d)
        apoded_ffted_2d = fft1d(apoded_2d)
    
        spec2d = fromPipe(self.filename)
        ffted_2d = fft1d(apoded_2d)
        ts.assert_equal(ffted_2d, apoded_ffted_2d, '2D Apodization unity with FFT failed')
    
    
    def test_apod_different_F1F2(self):
        dic, data = self.dic, self.data
        spec2d = fromPipe(self.filename)
        
        
        # 2D FFT using pipe_proc functions
        dic3, data3 = pipep.em(dic, data, 0.2)
        dic3, data3 = pipep.tp(dic3, data3, auto=True)
        dic3, data3 = pipep.gm(dic3, data3, 1, 0.5, 0.5)
        dic3, data3 = pipep.tp(dic3, data3, auto=True)
        
        # test auto class implementation
        apoded = apod(spec2d, F2_w1=lambda s: EM(s, 0.2), F1_w2=lambda s: GM(s, 1, 0.5, 0.5))
        ts.assert_equal(data3, apoded, '2D Apodized spectrum doesnt match pipe_proc.em and gm on F1 and F2')
