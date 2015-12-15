import unittest
import nmrglue as ng
from .icoshift import calculate_intervals, intervals2slices, slices2intervals, calculate_target, \
                      fft_crosscor, crosscor_shift, apply_shift, icoshift
import numpy.testing as ts
import numpy as np

class icoshift_test(unittest.TestCase):
    def setUp(self):
        sim1 = ng.linesh.sim_NDregion((256,),('l',), [[(100, 5)]], [100])
        sim2 = ng.linesh.sim_NDregion((256,),('l',), [[(120, 5)]], [100])
        sim3 = ng.linesh.sim_NDregion((256,),('l',), [[(85, 5)]], [100])
        self.sim_data = np.array([sim1, sim2, sim3])
        
        a = np.array([1,2,3,4,5])
        self.aligned_toy = np.array([a,a,a])
        self.toy = np.array([a,np.roll(a, 2),a])
    
    def test_calc_intervals(self):
        whole = calculate_intervals('whole', self.sim_data.shape[-1])
        self.assertSequenceEqual(whole, (0, 256), 'calculate_interval failed with the "whole" parameter %s' %str(whole))
        
        segs = calculate_intervals(16, self.sim_data.shape[-1])
        self.assertEqual(len(segs), 16, 'calculate_interval: incorrect No. of intervals %s' %len(segs))
        
        interv_list = calculate_intervals(segs, self.sim_data.shape[-1])
        ts.assert_array_equal(interv_list, segs, 'calculate_interval: failed when given a list as a parameter')
        
        slices = intervals2slices(segs, self.sim_data.shape[-1])
        self.assertEqual(len(slices), 16, 'intervals2slices: incorrect No. of slices %s' %len(slices))
        
        ts.assert_array_equal(slices2intervals(slices), segs, 'slices2intervals: couldnt produce the original intervals')
        
        data_copy = np.zeros_like(self.sim_data)
        for slice_ in slices:
            data_copy[:, slice_] = self.sim_data[:, slice_]
        
        ts.assert_array_equal(data_copy, self.sim_data, 'Interval slices dont cover the whole array')
        
        
    def test_calc_target(self):
        segs = calculate_intervals(16, self.sim_data.shape[-1])
        t = calculate_target(self.sim_data[1,:], self.sim_data, segs)
        ts.assert_array_equal(t, self.sim_data[1,:], 'calculate_target: failed when provided ndarray')
        
        with self.assertRaises(ValueError):
            calculate_target(self.sim_data[1,:-1], self.sim_data, segs)
        
        segs = [0,2,4]
        t = calculate_target('max', self.aligned_toy, segs)
        ts.assert_array_equal(t, self.aligned_toy[1,:], 'calculate_target: failed with paramter "max" on aligned data')
        
        t = calculate_target('average', self.aligned_toy, segs)
        ts.assert_array_equal(t, self.aligned_toy[1,:], 'calculate_target: failed with paramter "average" on aligned data')
        
        t = calculate_target('median', self.aligned_toy, segs)
        ts.assert_array_equal(t, self.aligned_toy[1,:], 'calculate_target: failed with paramter "median" on aligned data')
        
        
        ## Unaligned toy data
        t = calculate_target('max', self.toy, segs)
        ts.assert_array_equal(t, np.array([4,5,3,4,5]), 'calculate_target: failed with paramter "max" on toy data')
        
        t = calculate_target('average', self.toy, segs)
        ts.assert_array_equal(t, np.array([6,9,7,10,13])/3., 'calculate_target: failed with paramter "average" on toy data')
        
    def test_corsscor(self):
        fft = fft_crosscor(self.sim_data[0,:], self.sim_data)
        t = np.argmax(fft, axis=-1)
        ts.assert_array_equal(t, np.array([0, 492, 15]), 'crosscor_fft: incorrect maxima %s' %str(t))
        
        shifts = crosscor_shift(self.sim_data[0,:], self.sim_data)
        ts.assert_array_equal(shifts, np.array([0, -20, 15]), 'crosscor_shift: incorrect shifts %s' %str(shifts))
        
        shifts = crosscor_shift(self.sim_data[2,:], self.sim_data)
        ts.assert_array_equal(shifts, np.array([-15, -35, 0]), 'crosscor_shift: incorrect shifts (should be all -ve) %s' %str(shifts))
        
        shifts = crosscor_shift(self.sim_data[1,:], self.sim_data)
        ts.assert_array_equal(shifts, np.array([20, 0, 35]), 'crosscor_shift: incorrect shifts (should be all -ve) %s' %str(shifts))
        
        # n < both +ve and -ve
        shifts = crosscor_shift(self.sim_data[0,:], self.sim_data, n=10)
        ts.assert_array_equal(shifts, np.array([0, -10, 10]), 
            'crosscor_shift: incorrect shifts when n < both +ve and -ve %s' %str(shifts))
        
        # n < -ve
        shifts = crosscor_shift(self.sim_data[2,:], self.sim_data, n=20)
        ts.assert_array_equal(shifts, np.array([-15, -20, 0]), 
            'crosscor_shift: incorrect shifts when n < -ve %s' %str(shifts))
        
        # n < +ve
        shifts = crosscor_shift(self.sim_data[1,:], self.sim_data, n=25)
        ts.assert_array_equal(shifts, np.array([20, 0, 25]), 
            'crosscor_shift: incorrect shifts when n < +ve %s' %str(shifts))
    
    def test_apply_shifts(self):
        shifted = apply_shift(self.toy, [2,-2,3], fill_with_previous=True)
        expected = np.array([[1,1,1,2,3], [1,2,3,3,3], [1,1,1,1,2]])
        
        ts.assert_array_equal(shifted, expected, 'apply_shift: incorrect shifting')
        
        shifted = apply_shift(self.toy, [2,-2,3], fill_with_previous=False)
        expected = np.array(
                       [[np.nan,np.nan,1,2,3], [1,2,3,np.nan,np.nan], [np.nan,np.nan,np.nan,1,2]]
                   )
        
        ts.assert_array_equal(shifted, expected, 'apply_shift: incorrect filling with NaNs')
    
    