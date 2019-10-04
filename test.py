import unittest
from SlidingWindow import SlidingWindow
import BandEnum
import numpy as np
import rasterio

class TestSlidingWindow(unittest.TestCase):

    test_path = 'test.tif'
    test_path_dem = 'dem/gunsite_dem-2-1.tif'

    def no_test_aggregation(self):
        slide_window = SlidingWindow(self.test_path, BandEnum.rgbIr)
        img = rasterio.open(self.test_path)
        arr = img.read(1).astype(float)[0:512, 0:512]

        sum_all = slide_window._partial_aggregation(arr, 0, 7, '++++')
        partial_sum_all = slide_window._partial_aggregation(arr, 0, 2, '++++')
        partial_sum_all = slide_window._partial_aggregation(partial_sum_all, 2, 3, '++++')
        partial_sum_all = slide_window._partial_aggregation(partial_sum_all, 3, 7, '++++')
        brute_sum_all = slide_window._aggregation_brute(arr, '++++', 7)

        sum_bottom = slide_window._partial_aggregation(arr, 0, 7, '--++')
        partial_sum_bottom = slide_window._partial_aggregation(arr, 0, 2, '--++')
        partial_sum_bottom = slide_window._partial_aggregation(partial_sum_bottom, 2, 3, '--++')
        partial_sum_bottom = slide_window._partial_aggregation(partial_sum_bottom, 3, 7, '--++')
        brute_sum_bottom = slide_window._aggregation_brute(arr, '--++', 7)

        sum_right = slide_window._partial_aggregation(arr, 0, 7, '-+-+')
        partial_sum_right = slide_window._partial_aggregation(arr, 0, 2, '-+-+')
        partial_sum_right = slide_window._partial_aggregation(partial_sum_right, 2, 3, '-+-+')
        partial_sum_right = slide_window._partial_aggregation(partial_sum_right, 3, 7, '-+-+')
        brute_sum_right = slide_window._aggregation_brute(arr, '-+-+', 7)

        sum_main_diag = slide_window._partial_aggregation(arr, 0, 7, '+--+')
        partial_sum_main_diag = slide_window._partial_aggregation(arr, 0, 2, '+--+')
        partial_sum_main_diag = slide_window._partial_aggregation(partial_sum_main_diag, 2, 3, '+--+')
        partial_sum_main_diag = slide_window._partial_aggregation(partial_sum_main_diag, 3, 7, '+--+')
        brute_sum_main_diag = slide_window._aggregation_brute(arr, '+--+', 7)

        maximum = slide_window._partial_aggregation(arr, 0, 7, 'max')
        partial_maximum = slide_window._partial_aggregation(arr, 0, 2, 'max')
        partial_maximum = slide_window._partial_aggregation(partial_maximum, 2, 3, 'max')
        partial_maximum = slide_window._partial_aggregation(partial_maximum, 3, 7, 'max')
        brute_maximum = slide_window._aggregation_brute(arr, 'max', 7)

        minimum = slide_window._partial_aggregation(arr, 0, 7, 'min')
        partial_minimum = slide_window._partial_aggregation(arr, 0, 2, 'min')
        partial_minimum = slide_window._partial_aggregation(partial_minimum, 2, 3, 'min')
        partial_minimum = slide_window._partial_aggregation(partial_minimum, 3, 7, 'min')
        brute_minimum = slide_window._aggregation_brute(arr, 'min', 7)

        self.assertTrue(np.array_equal(sum_all, brute_sum_all))
        self.assertTrue(np.array_equal(partial_sum_all, brute_sum_all))

        self.assertTrue(np.array_equal(sum_bottom, brute_sum_bottom))
        self.assertTrue(np.array_equal(partial_sum_bottom, brute_sum_bottom))

        self.assertTrue(np.array_equal(sum_right, brute_sum_right))
        self.assertTrue(np.array_equal(partial_sum_right, brute_sum_right))

        self.assertTrue(np.array_equal(sum_main_diag, brute_sum_main_diag))
        self.assertTrue(np.array_equal(partial_sum_main_diag, brute_sum_main_diag))

        self.assertTrue(np.array_equal(maximum, brute_maximum))
        self.assertTrue(np.array_equal(partial_maximum, brute_maximum))

        self.assertTrue(np.array_equal(minimum, brute_minimum))
        self.assertTrue(np.array_equal(partial_minimum, brute_minimum))

    def no_test_regression(self):
        slide_window = SlidingWindow(self.test_path, BandEnum.rgbIr)
        img = rasterio.open(self.test_path)
        arr1 = img.read(1).astype(float)[0:128, 0:128]
        arr2 = img.read(2).astype(float)[0:128, 0:128]

        arr_good = slide_window._regression(arr1, arr2, 6)
        arr_good = np.round(arr_good, 10)
        arr_brute = slide_window._regression_brute(arr1, arr2, 6)
        arr_brute = np.round(arr_brute, 10)

        self.assertTrue(np.array_equal(arr_good, arr_brute))

    def test_dem(self):
        slide_window = SlidingWindow(self.test_path_dem, BandEnum.rgbIr)
        img = rasterio.open(self.test_path_dem)
        arr = img.read(1).astype(float)[0:1024, 0:1024]

        arr_dic = slide_window._initialize_arrays(arr)
        slide_window._double_w(1, arr_dic)
        slide_window._double_w(2, arr_dic)
        slide_window._double_w(3, arr_dic)
        slide_window._double_w(4, arr_dic)
        slide_window._double_w(5, arr_dic)
        slide_window._double_w(6, arr_dic)
        arr_dic_1 = {}
        for i in (['z', arr_dic['z']], ['xz', arr_dic['xz']], ['yz', arr_dic['yz']], ['xxz', arr_dic['xxz']], ['yyz', arr_dic['yyz']], ['xyz', arr_dic['xyz']]):
            arr_dic_1[i[0]] = np.round(i[1], 0)

        arr_dic = slide_window._initialize_arrays(arr)
        slide_window._double_w_brute(1, arr_dic)
        slide_window._double_w_brute(2, arr_dic)
        slide_window._double_w_brute(3, arr_dic)
        slide_window._double_w_brute(4, arr_dic)
        slide_window._double_w_brute(5, arr_dic)
        slide_window._double_w_brute(6, arr_dic)
        arr_dic_2 = {}
        for i in (['z', arr_dic['z']], ['xz', arr_dic['xz']], ['yz', arr_dic['yz']], ['xxz', arr_dic['xxz']], ['yyz', arr_dic['yyz']], ['xyz', arr_dic['xyz']]):
            arr_dic_2[i[0]] = np.round(i[1], 0)

        arr_dic = slide_window._initialize_arrays(arr)
        slide_window._double_w_old(1, arr_dic)
        slide_window._double_w_old(2, arr_dic)
        slide_window._double_w_old(3, arr_dic)
        slide_window._double_w_old(4, arr_dic)
        slide_window._double_w_old(5, arr_dic)
        slide_window._double_w_old(6, arr_dic)
        arr_dic_3 = {}
        for i in (['z', arr_dic['z']], ['xz', arr_dic['xz']], ['yz', arr_dic['yz']], ['xxz', arr_dic['xxz']], ['yyz', arr_dic['yyz']], ['xyz', arr_dic['xyz']]):
            arr_dic_3[i[0]] = np.round(i[1], 0)

        for key in arr_dic_1:
            self.assertTrue(np.array_equal(arr_dic_1[key], arr_dic_2[key]))

        for key in arr_dic_1:
            self.assertTrue(np.array_equal(arr_dic_1[key], arr_dic_3[key]))

if __name__ == '__main__':
    unittest.main()
