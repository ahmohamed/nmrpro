import unittest
import nmrglue as ng
from ...classes.NMRSpectrum import NMRSpectrum
from .AIBin import optimize_boundry, AIBin, VbScore
import numpy.testing as ts
from numpy import array, roll

class AIBin_1DTest(unittest.TestCase):
    def setUp(self):
        sim = ng.linesh.sim_NDregion((256,),('l',), [[(100, 5)], [(115, 5)]], [100,100])
        self.small_diff = array([sim, roll(sim,1), roll(sim,-2)])
        self.big_diff = array([sim, roll(sim,1), roll(sim,-10)])
    
    def test_VbScore(self):
        '''Testing the scoring function in AI binning algorithm'''
        #noise
        self.assertEqual(VbScore(self.small_diff) > 0, True, 'VbScore yielding 0 score for signal that contains peaks')
        #whole signal
        self.assertEqual(VbScore(self.small_diff[:, 0:95]) > 0, False, 'VbScore yielding non-zero score for signal without peaks')
    
    def test_sm_diff(self):
        '''Testing the ability of AI binning to group slightly misaligned peaks'''
        bins = optimize_boundry(array(self.small_diff), R=0.2)
        self.assertEqual(len(bins), 2, 'AI binning did not group slightly misaligned peaks together.')
        
    def test_big_diff(self):
        '''Testing the ability of AI binning to serparate largely misaligned peaks'''
        bins = optimize_boundry(array(self.big_diff), R=0.2)
        self.assertEqual(len(bins), 3, 'AI binning did not separate largely misaligned peaks together.')

    def test_AIbin_R(self):
        pass